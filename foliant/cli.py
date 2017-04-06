"""Foliant: Markdown to PDF, Docx, and LaTeX generator powered by Pandoc.

Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document> [--secret=<client_secret*.json>]
  foliant (swagger2markdown | s2m) <swagger-location> [--output=<output-file>]
    [--template=<jinja2-template>] [--additional=<swagger-location>]
  foliant (apidoc2markdown | a2m) <apidoc-location> [--output=<output-file>]
    [--template=<jinja2-template>]
  foliant (-h | --help)
  foliant --version

Options:
  -h --help                          Show this screen.
  -v --version                       Show version.
  -p --path=<project-path>           Path to your project [default: .].
  -s --secret=<client_secret*.json>  Path to Google app's client secret file.
  -o --output=<output-file>          Path to the converted Markdown file
                                     [default: api.md]
  -t --template=<jinja2-template>    Custom Jinja2 template for the Markdown
                                     output.
  -a --additional=<swagger-location> Complementary Swagger file to fill in
                                     missing values from the main one.
"""

from docopt import docopt
from foliant import builder, uploader, swagger2markdown, apidoc2markdown
from foliant import __version__ as foliant_version


def main():
    """Handles command-line params and runs the respective core function."""

    args = docopt(__doc__, version="Foliant %s (Python)" % foliant_version)

    if args["build"] or args["make"]:
        output_file = builder.build(args["<target>"], args["--path"])

        print("----")
        print("Result: %s" % output_file)

    elif args["upload"] or args["up"]:
        link = uploader.upload(args["<document>"])

        print("----")
        print("Link: %s" % link)

    elif args["swagger2markdown"] or args["s2m"]:
        swagger_location = args["<swagger-location>"]
        output_file = args["--output"]
        template_file = args.get("--template")
        additional_swagger_location = args.get("--additional")
        swagger2markdown.convert(
            swagger_location,
            output_file,
            template_file,
            additional_swagger_location
        )

        print("---")
        print("Result: %s" % output_file)

    elif args["apidoc2markdown"] or args["a2m"]:
        apidoc_location = args["<apidoc-location>"]
        output_file = args["--output"]
        template_file = args.get("--template")
        apidoc2markdown.convert(apidoc_location, output_file, template_file)

        print("---")
        print("Result: %s" % output_file)
