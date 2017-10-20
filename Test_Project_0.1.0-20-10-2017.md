# Test Project

Welcome to Foliant, a documentation builder with superpowers.


## Usage



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

[Learn more in the docs →](docs/README.md)


{{.Mrf}}

# Sample Diagram

![Caption](diagrams/seqdiag/8ad0b44a-19e5-4ca9-87d5-b73529e0236e.png)

## International Characters

Привет, Фолиант!

