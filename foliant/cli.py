"""Foliant: Markdown to PDF, Docx, and LaTeX generator powered by Pandoc.

Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document> [--secret=<client_secret*.json>]
  foliant (-h | --help)
  foliant --version

Options:
  -h --help                          Show this screen.
  -v --version                       Show version.
  -p --path=<project-path>           Path to your project [default: .].
  -s --secret=<client_secret*.json>  Path to Google app's client secret file.
"""

from docopt import docopt
import colorama
from colorama import Fore

from . import builder, uploader
from . import __version__ as foliant_version


def main():
    """Handles command-line params and runs the respective core function."""

    colorama.init(autoreset=True)

    args = docopt(__doc__, version="Foliant %s (Python)" % foliant_version)

    if args["build"] or args["make"]:
        result = builder.build(args["<target>"], args["--path"])

    elif args["upload"] or args["up"]:
        result = uploader.upload(args["<document>"])

    print("---")
    print(Fore.GREEN + "Result: %s" % result)

    colorama.deinit()
