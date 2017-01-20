import re


def process_remote_include(repo, path, from_heading, to_heading, options={}):
    print("Remote include")
    print("Repo: %s" % repo)
    print("Path: %s" % path)
    print("From heading: %s" % from_heading)
    print("To_heading: %s" % to_heading)
    print("Options: %s" % options)


def process_local_include(path, from_heading, to_heading, options={}):
    print("Local include")
    print("Path: %s" % path)
    print("From heading: %s" % from_heading)
    print("To_heading: %s" % to_heading)
    print("Options: %s" % options)


def convert_value(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def extract_options(options_line):
    if not options_line:
        return None

    options = {}

    for option in (option.strip() for option in options_line.split(',')):
        option_parts = option.split(':')
        if len(option_parts) == 1:
            options[option_parts[0]] = True
        elif len(option_parts) == 2:
            options[option_parts[0]] = convert_value(option_parts[1])

    return options


def process_includes(content):
    include_statement = re.compile(
        r"\{\{\s*(<(?P<repo>.+)\>)?" +
        r"(?P<path>.+?)(\#(?P<from_heading>.+?)(:(?P<to_heading>.+?))?)?" +
        r"\s*(\|\s*(?P<options>.+))?\s*\}\}"
    )

    for include in re.finditer(include_statement, content):
        if include.group("repo"):
            process_remote_include(
                include.group("repo"),
                include.group("path"),
                include.group("from_heading"),
                include.group("to_heading"),
                extract_options(include.group("options"))
            )
        else:
            process_local_include(
                include.group("path"),
                include.group("from_heading"),
                include.group("to_heading"),
                extract_options(include.group("options"))
            )

    return content


if __name__ == "__main__":
    process_includes("""This is a sample that includes an include statement:

{{ <myrepo>/path/to/file.md#heading1:heading2 | nohead, sethead:3 }}

Another one:

{{../path/to/file.md#heading1}}

Here's some text after it.
""")
