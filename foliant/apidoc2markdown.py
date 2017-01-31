from __future__ import print_function

"""Apidoc to Markdown converter."""

import sys
import subprocess


def convert(apidoc_location, output_file, template_file):
    """Convert Apidoc JSON files to Markdown."""

    if template_file:
        a2m_command = "apidoc2markdown -i %s -o %s -t %s" % (
            apidoc_location,
            output_file,
            template_file
        )

    else:
        a2m_command = "apidoc2markdown -i %s -o %s" % (
            apidoc_location,
            output_file
        )

    print("Baking output... ", end='')
    sys.stdout.flush()

    try:
        proc = subprocess.check_output(
            a2m_command,
            stderr=subprocess.PIPE,
            shell=True
        )

        print("Done!")

    except subprocess.CalledProcessError as e:
        quit(e.stderr.decode())
