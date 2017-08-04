from __future__ import print_function

"""Seqdiag processor."""

import sys
import os
from os.path import join
import subprocess
from uuid import uuid4


def process_seqdiag_block(sd_block, sd_id, src_dir, sd_dir):
    """Extract diagram definition, convert it to image,
    and return the image ref.
    """

    sd_src_filename = "%s.diag" % sd_id
    sd_content = '\n'.join(sd_block[1: -1])
    sd_caption = sd_block[0].replace("```seqdiag", '').strip()
    sd_img_ref = "![%s](%s/%s.png)" % (sd_caption, sd_dir, sd_id)
    sd_src_path = join(src_dir, sd_dir, sd_src_filename)
    sd_command = "seqdiag -a %s" % sd_src_path

    with open(sd_src_path, 'w', encoding="utf8") as sd_src_file:
        sd_src_file.writelines(sd_content)

    try:
        subprocess.check_output(
            sd_command,
            stderr=subprocess.PIPE,
            shell=True
        )

    except subprocess.CalledProcessError as e:
        print("Processing diagram %s failed: %s" % (sd_src_path, e))

    return sd_img_ref


def process_diagrams(src_dir, src_file):
    """Find seqdiag code blocks, feed their content to seqdiag tool,
    and replace them with image references.
    """

    print("Drawing diagrams... ", end='')
    sys.stdout.flush()

    sd_dir = "diagrams"
    src_path = join(src_dir, src_file)
    buffer, new_source = [], []
    sd_id = uuid4()

    if not os.path.exists(join(src_dir, sd_dir)):
        os.makedirs(join(src_dir, sd_dir))

    with open(src_path, encoding="utf8") as src:
        for line in (l.rstrip() for l in src):
            if not buffer:
                if line.startswith("```seqdiag"):
                    buffer.append(line)
                else:
                    new_source.append(line)

            else:
                buffer.append(line)

                if line == "```":
                    new_source.append(
                        process_seqdiag_block(
                            buffer,
                            sd_id,
                            src_dir,
                            sd_dir
                        )
                    )
                    sd_id = uuid4()
                    buffer = []

    with open(src_path, 'w', encoding="utf8") as src:
        src.writelines('\n'.join(new_source))

    print("Done!")
