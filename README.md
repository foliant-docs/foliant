[![Build Status](https://travis-ci.org/foliant-docs/foliant.svg?branch=master)](https://travis-ci.org/foliant-docs/foliant)

# Foliant

**Foliant** is a documentation generator that builds PDF, Docx, and TeX documents from Markdown source.

TL;DR:

```shell
$ cookiecutter gh:foliant-docs/cookiecutter-foliant
...
$ cd my-project
$ docker run --rm -v `pwd`:/usr/src/app -w /usr/src/app foliant/foliant make pdf
Collecting source... Done!
Drawing diagrams... Done!
Baking output... Done!
----
Result: My_Project_0.1.0-26-08-2017.pdf
```

[Learn more in the wiki →](https://github.com/foliant-docs/foliant/wiki)
