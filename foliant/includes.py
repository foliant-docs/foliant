"""Include processor."""

import re
import errno
import os
import os.path as ospa
from io import StringIO

from . import gitutils


IMAGE_DIRS = ("", "images", "graphics")
IGNORE_DIRS = (".git", ".venv", ".vscode", "__pycache__", "foliantcache")

HEADING_PATTERN = re.compile(
    r"^(?P<hashes>\#+)\s*(?P<title>[^\#]+)\s*$",
    flags=re.MULTILINE
)
IMAGE_PATTERN = re.compile(r"\!\[(?P<caption>.*)\]\((?P<path>.+)\)")
INCLUDE_PATTERN = re.compile(
    r"\{\{\s*(\<(?P<repo>[^\#^\>]+)(#(?P<revision>[^\>]+))?\>)?" +
    r"(?P<path>[^\#]+?)" +
    r"(\#(?P<from_heading>[^:]*?)(:(?P<to_heading>.+?))?)?" +
    r"\s*(\|\s*(?P<options>.+))?\s*\}\}"
)


def convert_value(value):
    """Attempt to convert a string to integer, float, or boolean. If nothing
    matches, return the original string.
    """

    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            try:
                return bool(value)
            except ValueError:
                return value


def extract_options(options_line):
    """Extract include options as a dictionary from a raw string.

    Options without values are treated as having boolean ``True`` value.
    """

    options = {}

    if not options_line:
        return options

    for option in (option.strip() for option in options_line.split(',')):
        option_parts = option.split(':')
        if len(option_parts) == 1:
            options[option_parts[0]] = True
        elif len(option_parts) == 2:
            options[option_parts[0]] = convert_value(option_parts[1])

    return options


def shift_headings(content, shift):
    """Shift all Markdown headings in a string by a given value. The shift can
    be positive or negative.
    """

    def sub(heading):
        new_heading_level = len(heading.group("hashes")) + shift
        return "%s %s" % ('#' * new_heading_level, heading.group("title"))

    return HEADING_PATTERN.sub(sub, content)


def find_top_heading_level(content):
    """Find the highest level heading (i.e. having the least '#'s)
    in a Markdown string."""

    result = float("inf")

    for heading in HEADING_PATTERN.findall(content):
        heading_level = heading.count("#")

        if heading_level < result:
            result = heading_level

    return result if result < float("inf") else 0


def adjust_headings(content, from_heading, to_heading=None,
                    options={}):
    """Cut part of Markdown string between two headings, set heading level,
    and remove top heading.

    If only the starting heading is defined, cut to the next heading
    of the same level. If no headings are defined, return the full string.

    Heading shift and top heading elimination are optional.
    """

    if from_heading:
        from_heading_pattern = re.compile(
            r"^\#+\s*%s\s*$" % from_heading,
            flags=re.MULTILINE
        )

        if not from_heading_pattern.findall(content):
            return ""

        from_heading_line = from_heading_pattern.findall(content)[0]
        from_heading_level = from_heading_line.count('#')

        result = from_heading_pattern.split(content)[1]

        if to_heading:
            to_heading_pattern = re.compile(
                r"^\#+\s*%s\s*$" % to_heading,
                flags=re.MULTILINE
            )

        else:
            to_heading_pattern = re.compile(
                r"^\#{1,%d}[^\#]+?$" % from_heading_level,
                flags=re.MULTILINE
            )

        result = to_heading_pattern.split(result)[0]

        if not options.get("nohead"):
            result = from_heading_line + result

        if options.get("sethead"):
            if options["sethead"] > 0:
                result = shift_headings(
                    result,
                    options["sethead"] - from_heading_level
                )

        return result

    else:
        content_buffer = StringIO(content)

        first_line = content_buffer.readline()

        if HEADING_PATTERN.fullmatch(first_line):
            from_heading_line = first_line
            from_heading_level = from_heading_line.count('#')
            result = content_buffer.read()

        else:
            from_heading_line = ''
            from_heading_level = find_top_heading_level(content)
            result = content

        if to_heading:
            to_heading_pattern = re.compile(
                r"^\#+\s*%s\s*$" % to_heading,
                flags=re.MULTILINE
            )
            result = to_heading_pattern.split(result)[0]

        if not options.get("nohead"):
            result = from_heading_line + result

        if options.get("sethead"):
            if options["sethead"] > 0:
                result = shift_headings(
                    result,
                    options["sethead"] - from_heading_level
                )

        return result


def find_image(image_path, start_dir, target_dir):
    """Locate an image in the disk based on the path from the image directive
    and the path to the directory with the document containing the image.

    The function looks for the image first in the document directory and then
    in all upper-level directories until it finds the image or reaches root.
    In each location, it checks the directory itself and the subdirectories
    ``images`` and ``graphics`` (defined in ``IMAGE_DIRS``).

    The result is adjusted relative to the target directory where the final
    document will be built.
    """

    def normabspath(path):
        return ospa.normcase(ospa.abspath(path))

    def is_root(path):
        return '' in ospa.split(normabspath(path))

    def normalize(path):
        return '/'.join(path.split(ospa.sep))

    def adjust(path):
        return ospa.relpath(path, target_dir)

    level = 0
    lookup_dir = ospa.join(start_dir, "../" * level)

    while not is_root(lookup_dir):
        for image_dir in (
            ospa.join(lookup_dir, image_dir) for image_dir in IMAGE_DIRS
        ):
            if ospa.isfile(ospa.join(image_dir, image_path)):
                return normalize(adjust(ospa.join(image_dir, image_path)))

        level += 1
        lookup_dir = ospa.join(start_dir, "../" * level)

    return '.'


def adjust_image_paths(content, lookup_dir, target_dir):
    """Locate all images referenced in a string and replace their paths
    with valid Markdown paths that point to the images relative to the target
    directory.

    ``lookup_dir`` is the starting point to look for the images—the directory
    with the document.
    """

    def sub(image):
        image_caption = image.group("caption")
        image_path = image.group("path")

        adjusted_image_path = find_image(image_path, lookup_dir, target_dir)

        return "![%s](%s)" % (image_caption, adjusted_image_path)

    return IMAGE_PATTERN.sub(sub, content)


def find_incl_file(incl_file_name, lookup_dir):
    lookup_dir_contents = os.listdir(lookup_dir)

    if incl_file_name in lookup_dir_contents:
        return ospa.join(lookup_dir, incl_file_name)
    else:
        child_dirs = (
            child for child in os.listdir(lookup_dir)
            if ospa.isdir(ospa.join(lookup_dir, child))
            and child not in IGNORE_DIRS
        )
        for child_dir in child_dirs:
            incl_file = find_incl_file(
                incl_file_name,
                ospa.join(lookup_dir, child_dir)
            )

            if incl_file:
                return incl_file

        return None


def process_local_include(path, from_heading, to_heading, options, sources_dir,
                          target_dir):
    """Replace a local include statement with the file content. Necessary
    adjustments are applied to the content: cut between certain headings,
    strip the top heading, set heading level.
    """

    incl_file_path = ospa.join(sources_dir, path)
    incl_file_dir, incl_file_name = ospa.split(incl_file_path)

    if incl_file_name.startswith('^'):
        adjusted_incl_file_path = find_incl_file(
            incl_file_name[1:],
            incl_file_dir
        )

        if not adjusted_incl_file_path:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), incl_file_path
            )

        incl_file_dir, incl_file_name = ospa.split(adjusted_incl_file_path)

    else:
        adjusted_incl_file_path = incl_file_path

    with open(adjusted_incl_file_path, encoding="utf8") as incl_file:
        incl_content = incl_file.read()

        incl_content = adjust_headings(
            incl_content,
            from_heading,
            to_heading,
            options
        )

        incl_content = adjust_image_paths(
            incl_content,
            incl_file_dir,
            target_dir
        )

    return incl_content


def process_remote_include(repo, revision, path, from_heading, to_heading,
                           options, sources_dir, target_dir):
    """Please a remote include statement with the file content. This involves
    cloning or updating the git repository with the file and processing
    the include as a regular local one.
    """

    repo_path = gitutils.sync_repo(repo, target_dir, revision)

    return process_local_include(
        ospa.relpath(ospa.join(repo_path, path), sources_dir),
        from_heading,
        to_heading,
        options,
        sources_dir,
        target_dir
    )


def process_includes(content, sources_dir, target_dir, cfg):
    """Replace all include statements with the respective file content."""

    def sub(include, sources_dir=sources_dir):
        try:
            if include.group("repo"):
                repo = include.group("repo")
                repo_url = cfg.get("git", {}).get(repo) or repo

                return process_remote_include(
                    repo_url,
                    include.group("revision") or "master",
                    include.group("path"),
                    include.group("from_heading"),
                    include.group("to_heading"),
                    extract_options(include.group("options")),
                    sources_dir,
                    target_dir
                )
            else:
                return process_local_include(
                    include.group("path"),
                    include.group("from_heading"),
                    include.group("to_heading"),
                    extract_options(include.group("options")),
                    sources_dir,
                    target_dir
                )

        except FileNotFoundError as exception:
            print(
                "\n\tWarning: File '%s' does not exist." % exception.filename
            )

    result = INCLUDE_PATTERN.sub(sub, content)

    if INCLUDE_PATTERN.search(result):
        return process_includes(result, sources_dir, target_dir, cfg)
    else:
        return result
