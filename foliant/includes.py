import re
import os.path as ospa
from io import StringIO

from . import gitutils


IMAGE_DIRS = ("", "images", "graphics")


def convert_value(value):
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
    def sub(heading):
        new_heading_level = len(heading.group("hashes")) + shift
        return "%s %s" % ('#' * new_heading_level, heading.group("title"))

    heading_pattern = re.compile(
        r"^(?P<hashes>\#+)\s*(?P<title>[^\#]+)\s*$",
        flags=re.MULTILINE
    )

    return heading_pattern.sub(sub, content)


def find_top_heading_level(content):
    heading_pattern = re.compile(r"^\#+[^\#]+?$", flags=re.MULTILINE)

    result = float("inf")

    for heading in heading_pattern.findall(content):
        heading_level = heading.count("#")

        if heading_level < result:
            result = heading_level

    return result if result < float("inf") else 0


def adjust_headings(content, from_heading, to_heading=None,
                    options={}):
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
        from_heading_pattern = re.compile(r"^\#+[^\#]+?$")

        content_buffer = StringIO(content)

        first_line = content_buffer.readline()

        if from_heading_pattern.fullmatch(first_line):
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
    def is_root(path):
        return '' in ospa.split(ospa.abspath(path))

    def normabspath(path):
        return ospa.normcase(ospa.abspath(path))

    def normalize(path):
        return '/'.join(path.split(ospa.sep))

    def adjust(path):
        return ospa.relpath(path, target_dir)

    level = 0
    lookup_dir = ospa.join(start_dir, "../" * level)

    while not is_root(normabspath(lookup_dir)):
        for image_dir in (
            ospa.join(lookup_dir, image_dir) for image_dir in IMAGE_DIRS
        ):
            if ospa.isfile(ospa.join(image_dir, image_path)):
                return normalize(adjust(ospa.join(image_dir, image_path)))

        level += 1
        lookup_dir = ospa.join(start_dir, "../" * level)

    return ''


def adjust_images(content, lookup_dir, target_dir):
    def sub(image):
        image_caption = image.group("caption")
        image_path = image.group("path")

        adjusted_image_path = find_image(image_path, lookup_dir, target_dir)

        return "![%s](%s)" % (image_caption, adjusted_image_path)

    image_pattern = re.compile(r"\!\[(?P<caption>.*)\]\((?P<path>.+)\)")

    return image_pattern.sub(sub, content)


def process_local_include(path, from_heading, to_heading, options, sources_dir,
                          target_dir):
    with open(ospa.join(sources_dir, path), encoding="utf8") as incl_file:
        incl_content = incl_file.read()

        incl_content = adjust_headings(
            incl_content,
            from_heading,
            to_heading,
            options
        )

        incl_content = adjust_images(
            incl_content,
            ospa.split(ospa.join(sources_dir, path))[0],
            target_dir
        )

    return incl_content


def process_remote_include(repo, revision, path, from_heading, to_heading,
                           options, sources_dir, target_dir):
    repo_path = gitutils.sync_repo(repo, target_dir, revision)

    return process_local_include(
        ospa.join(repo_path, path),
        from_heading,
        to_heading,
        options,
        sources_dir,
        target_dir
    )


def process_includes(content, sources_dir, target_dir, cfg):
    def sub(include, sources_dir=sources_dir):
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

    include_pattern = re.compile(
        r"\{\{\s*(<(?P<repo>.+)@(?P<revision>.+)\>)?" +
        r"(?P<path>[^\#]+?)" +
        r"(\#(?P<from_heading>[^:]*?)(:(?P<to_heading>.+?))?)?" +
        r"\s*(\|\s*(?P<options>.+))?\s*\}\}"
    )

    return include_pattern.sub(sub, content)


if __name__ == "__main__":
    test_content = """Local include:

{{test-project/sources/chapter1.md#Aliquam quis accumsan mauris:Integer in hendrerit est | nohead, sethead:2 }}

Remote include:

{{ <ds@master>02_old_itv/01_descriptions/03_ui/client_products_android_app_interface_full_description.md }}

"""

    print(process_includes(test_content, cfg={"git":{"ds": "git://git.restr.im/docs-itv/doorstopper_itv.git"}}))
