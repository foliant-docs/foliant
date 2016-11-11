"""
Foliant: Markdown to PDF, Docx, and LaTeX generator powered by Pandoc.

Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document> [--secret=<client_secret*.json>]
  foliant (swagger2markdown | s2m) <swagger-location> [--output=<output-file>]
    [--template=<jinja2-template>]
  foliant (-h | --help)
  foliant --version

Options:
  -h --help                         Show this screen.
  -v --version                      Show version.
  -p --path=<project-path>          Path to your project [default: .].
  -s --secret=<client_secret*.json> Path to Google app's client secret file.
  -o --output=<output-file>         Path to the converted Markdown file
                                    [default: swagger.md]
  -t --template=<jinja2-template>   Custom Jinja2 template for the Markdown
                                    output.
"""

from docopt import docopt
import foliant.builder as builder
import foliant.uploader as uploader
import foliant.swagger2markdown as swagger2markdown
import foliant

def main():
    args = docopt(__doc__, version=foliant.__version__)

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
        config_file = args.get("--template")
        swagger2markdown.convert(swagger_location, output_file, config_file)

        print("---")
        print("Result: %s" % output_file)
