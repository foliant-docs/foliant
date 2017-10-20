# Adding a Diagram Backend

Starting with Foliant 0.4.2, adding new diagram backends is next to trivial.

You have the submodule `foliant.diagrams` that finds diagram definitions and feeds them to *diagram processors*. A diagram processor is a submodule of `foliant.diagrams` that is responsible for turning the diagram definition into an actual image of a diagram.

A diagram processor must implement `process_diagram(caption, body, src_dir, diag_dir_name, diag_id)` function. Typically, this function just calls a shell command corresponding to the diagram type. 

Here's a quick tutorial that will help you learn how to implement support of a diagram backend in Foliant. We will use PlantUML as an example. 

1. Copy `seqdiag.py` from `foliant/diagrams` to `foliant/diagrams/plantuml.py`. Here's what's in this file:

```python
"""Seqdiag processor."""

import subprocess
from os.path import join

from colorama import Fore


SEQDIAG_COMMAND = "seqdiag -a"


def process_diagram(caption, body, src_dir, diag_dir_name, diag_id):
    """Save diagram body to .diag file, draw PNG from it with seqdiag,
    and return the image ref."""

    diag_src_path = join(src_dir, diag_dir_name, "%s.diag" % diag_id)

    with open(diag_src_path, 'w', encoding="utf8") as diag_src:
        diag_src.write(body)

    try:
        subprocess.check_output(
            "%s %s" % (SEQDIAG_COMMAND, diag_src_path),
            stderr=subprocess.PIPE,
            shell=True
        )
    except subprocess.CalledProcessError as exception:
        print(
            Fore.YELLOW + "\nWarning: Processing of diagram %s failed: %s"
            % (diag_src_path, exception)
        )

    return "![%s](%s/%s.png)" % (caption, diag_dir_name, diag_id)

```

2. Replace seqdiag invocations with respective PlantUML ones:

```diff
- """Seqdiag processor."""
+ """PlantUML processor."""

import subprocess
from os.path import join

from colorama import Fore


- SEQDIAG_COMMAND = "seqdiag -a"
+ PLANTUML_COMMAND = "plantuml"


def process_diagram(caption, body, src_dir, diag_dir_name, diag_id):
-    """Save diagram body to .diag file, draw PNG from it with seqdiag,
+    """Save diagram body to .diag file, draw PNG from it with plantuml,
    and return the image ref."""

    diag_src_path = join(src_dir, diag_dir_name, "%s.diag" % diag_id)

    with open(diag_src_path, 'w', encoding="utf8") as diag_src:
        diag_src.write(body)

    try:
        subprocess.check_output(
-            "%s %s" % (SEQDIAG_COMMAND, diag_src_path),
+            "%s %s" % (PLANTUML_COMMAND, diag_src_path),
            stderr=subprocess.PIPE,
            shell=True
        )
    except subprocess.CalledProcessError as exception:
        print(
            Fore.YELLOW + "\nWarning: Processing of diagram %s failed: %s"
            % (diag_src_path, exception)
        )

    return "![%s](%s/%s.png)" % (caption, diag_dir_name, diag_id)
```

3. Register the new module in `foliant/diagrams/__init__.py`:

```diff
...
- from . import seqdiag
+ from . import seqdiag, plantuml
...
DIAG_BACKENDS = {
    "seqdiag": seqdiag.process_diagram,
+    "plantuml": plantuml.process_diagram,
}
```

4. Add PlantUML to the list of dependencies in the Dockerfile:

```diff
...
RUN apt-get install -y git
+ RUN apt-get install -y plantuml
RUN apt-get install -y python3 python3-pip
```
