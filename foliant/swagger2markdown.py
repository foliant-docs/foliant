from __future__ import print_function

"""Swagger to Markdown converter."""

import subprocess

def convert(swagger_location, output_file, template_file):
    """Convert Swagger JSON file to Markdown."""

    if template_file:
        s2m_command = "swagger2markdown -i %s -o %s -t %s" % (
            swagger_location,
            output_file,
            template_file
        )

    else:
        s2m_command = "swagger2markdown -i %s -o %s" % (
            swagger_location,
            output_file
        )

    print("Baking output... ", end='')

    try:
        proc = subprocess.check_output(
            s2m_command,
            stderr=subprocess.PIPE,
            shell=True
        )

        print("Done!")

    except subprocess.CalledProcessError as e:
        quit(e.stderr.decode())
