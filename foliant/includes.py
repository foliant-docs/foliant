import re
import os.path


def convert_value(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
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
        r"^(?P<hashes>\#+)\s*(?P<title>.+)$",
        flags=re.MULTILINE
    )

    return heading_pattern.sub(sub, content)


def process_headings(content, from_heading, to_heading=None,
                     options={}):
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
            r"^\#{1,%d}[^\#]+$" % from_heading_level,
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


def process_local_include(path, from_heading=None, to_heading=None,
                          options={}):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(current_dir, path), encoding="utf8") as incl_file:
        incl_content = incl_file.read()

        if from_heading:
            incl_content = process_headings(
                incl_content,
                from_heading,
                to_heading,
                options
            )

    return incl_content


def process_remote_include(repo, path, from_heading, to_heading, options={}):
    return "Remote"


def expand_include(include):
    if include.group("repo"):
        return process_remote_include(
            include.group("repo"),
            include.group("path"),
            include.group("from_heading"),
            include.group("to_heading"),
            extract_options(include.group("options"))
        )
    else:
        return process_local_include(
            include.group("path"),
            include.group("from_heading"),
            include.group("to_heading"),
            extract_options(include.group("options"))
        )


def process_includes(content):
    include_pattern = re.compile(
        r"\{\{\s*(<(?P<repo>.+)\>)?" +
        r"(?P<path>.+?)(\#(?P<from_heading>.+?)(:(?P<to_heading>.+?))?)?" +
        r"\s*(\|\s*(?P<options>.+))?\s*\}\}"
    )

    return include_pattern.sub(expand_include, content)


if __name__ == "__main__":
    test_content = """This is a sample that includes an include statement:

{{ <myrepo>/path/to/file.md#heading1:heading2 | nohead, sethead:3 }}

Another one:

{{../test-project/sources/chapter1.md#Cras scelerisque tincidunt bibendum | sethead:2 }}

Here's some text after it.
"""

    print(process_includes(test_content))
