"""Swagger to Markdown converter."""

import shlex, subprocess

def convert(swagger_location, output_file, template_file):
    """Convert Swagger JSON file to Markdown."""

    if template_file:
        command = "swagger2markdown -i %s -o %s -t %s" % (
            swagger_location,
            output_file,
            template_file
        )

    else:
        command = "swagger2markdown -i %s -o %s" % (
            swagger_location,
            output_file
        )

    print("Baking output... ", end='')

    try:
        proc = subprocess.check_output(
            shlex.split(command),
            stderr=subprocess.PIPE
        )

        print("Done!")

    except subprocess.CalledProcessError as e:
        quit(e.stderr.decode())
