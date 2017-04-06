from __future__ import print_function

"""Swagger to Markdown converter."""

import subprocess

def convert(swagger_location, output_file, template_file,
            additional_swagger_location):
    """Convert Swagger JSON file to Markdown."""

    s2m_command = "swagger2markdown -i %s -o %s" % (
        swagger_location,
        output_file
    )

    if template_file:
        s2m_command += " -t %s" % template_file

    if additional_swagger_location:
        s2m_command += " -a %s" % additional_swagger_location

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
