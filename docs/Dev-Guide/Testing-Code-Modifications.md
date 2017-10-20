# Testing Code Modifications

When you're working with the Foliant code, you need a quick way to see how your modifications affect its behavior.

First, you'll need a test project to run Foliant on. The easiest way to do it is with Cookiecutter:

```shell
$ cookiecutter gh:foliant-docs/cookiecutter-foliant 
```

To test code modifications, create a file called `run.py` in the repository root with the following content:

```python
from foliant import cli

cli.main()

```

Then run `run.py` with Python the same way you would run `foliant` command:

```shell
$ python run.py
Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document> [--secret=<client_secret*.json>]
  foliant (swagger2markdown | s2m) <swagger-location> [--output=<output-file>]
    [--template=<jinja2-template>] [--additional=<swagger-location>]
  foliant (apidoc2markdown | a2m) <apidoc-location> [--output=<output-file>]
    [--template=<jinja2-template>]
  foliant (-h | --help)
  foliant --version
```
