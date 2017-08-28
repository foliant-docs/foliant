"""Diagram processor."""

import sys
import os
from os.path import join
import re
from uuid import uuid4

from . import seqdiag, plantuml


DIAG_BACKENDS = {
    "seqdiag": seqdiag.process_diagram,
    "plantuml": plantuml.process_diagram,
}
DIAG_PATTERN = re.compile(
    r"^```(?P<kind>%s)(?P<caption>.*?)$(?P<body>.*?)```$"
    % "|".join(DIAG_BACKENDS.keys()),
    flags=re.MULTILINE|re.DOTALL
)
DIAG_DIR_NAME = "diagrams"


def process_diagrams(src_dir, src_file):
    """Find diagram definitions and replace them with image refs.
    The definitions are fed to processors that convert them into images"""

    def sub(include):
        return DIAG_BACKENDS[include.group("kind")](
            include.group("caption").lstrip(),
            include.group("body"),
            src_dir,
            DIAG_DIR_NAME,
            uuid4()
        )

    print("Drawing diagrams... ", end='')
    sys.stdout.flush()

    os.makedirs(join(src_dir, DIAG_DIR_NAME), exist_ok=True)

    src_path = join(src_dir, src_file)

    with open(src_path, encoding="utf8") as src:
        result = DIAG_PATTERN.sub(sub, src.read())

    with open(src_path, 'w', encoding="utf8") as src:
        src.write(result)

    print("Done!")
