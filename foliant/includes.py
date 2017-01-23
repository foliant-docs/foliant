import re
import os.path


def _convert_value(value):
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
            options[option_parts[0]] = _convert_value(option_parts[1])

    return options


def cut_by_headings(content, from_heading, to_heading=None,
                    keep_from_heading=True):
    from_heading_pattern = re.compile(
        r"^\#+\s*%s$" % from_heading,
        flags=re.MULTILINE
    )

    if not from_heading_pattern.findall(content):
        return ""

    from_heading_line = from_heading_pattern.findall(content)[0]

    result = from_heading_pattern.split(content)[1]

    if to_heading:
        to_heading_pattern = re.compile(
            r"^\#+\s*%s" % to_heading,
            flags=re.MULTILINE
        )

    else:
        from_heading_level = from_heading_line.count('#')
        to_heading_pattern = re.compile(
            r"^\#{1,%d}\s*.+$" % from_heading_level,
            flags=re.MULTILINE
        )

    result = to_heading_pattern.split(result)[0]

    if keep_from_heading:
        result = from_heading_line + result

    return result


def process_local_include(path, from_heading=None, to_heading=None,
                          options={}):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(current_dir, path), encoding="utf8") as incl_file:
        incl_content = incl_file.read()

        if from_heading:
            incl_content = cut_by_headings(
                incl_content,
                from_heading,
                to_heading,
                keep_from_heading=not options.get("nohead")
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

{{../test-project/sources/chapter1.md#Cras scelerisque tincidunt bibendum}}

Here's some text after it.
"""

    print(process_includes(test_content))
