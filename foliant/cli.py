"""
Foliant: Markdown to PDF, Docx, and LaTeX generator powered by Pandoc.

Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document>
  foliant (-h | --help)
  foliant --version

Options:
  -h --help                         Show this screen.
  -v --version                      Show version.
  -p --path=<project-path>          Path to your project [default: .].
"""

from docopt import docopt
import foliant.builder as builder
import foliant.uploader as uploader
import foliant

def main():
    args = docopt(__doc__, version=foliant.__version__)

    if args["build"] or args["make"]:
        output_file = builder.build(args["<target>"], args["--path"])
        print("Result: %s" % output_file)

    elif args["upload"] or args["up"]:
        link = uploader.upload(args["<document>"])
        print("Link: %s" % link)
