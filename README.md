# Foliant

Foliant is a all-in-one documentation authoring tool. It lets you produce standalone documents in pdf and docx, as well as websites, from single Markdown source.

Foliant is a _higher order_ tool, which means that it uses other programs to do its job. For pdf and docx, it uses [Pandoc](http://pandoc.org/), for websites it uses [MkDocs](http://www.mkdocs.org/).

Foliant preprocessors let you include parts of documents in other documents, show and hide content with flags, render diagrams from text, and more.

## Quickstart

Foliant is written in Python and requires Python 3.6.

1. Install Foliant, `init` extension, and `mkdocs` backend with pip:

```shell
$ pip install foliant foliantcontrib.mkdocs foliantcontrib.init
```

2. Create a new project with `foliant init`:

```shell
$ foliant init
Enter the project name: Hello Foliant
✔ Generating Foliant project
─────────────────────
Project "Hello Foliant" created in /path/to/hello-foliant
```

This command creates a basic Foliant project:

```shell
$ tree hello-foliant/
hello-foliant/
├── foliant.yml
├── pandoc.yml
└── src
    └── index.md

1 directory, 3 files
```

`foliant.yml` is the main config file. `pandoc.yml` lists commonly used Markdown extensions for Pandoc.

`src` directory holds the project source files. Initially, there's just one file `index.md`:

```markdown
# Welcome to Foliant

## Usage

<include sethead="2" nohead="true">
  $foliant$README.md#Foliant
</include>
```

`<include>` tags are processed by `includes` preprocessor and will be replaced with actual Markdown content on project build.

3. Build a website from the newly created project:

```shell
$ foliant make site -p hello-foliant/
✔ Parsing config
✔ Applying preprocessor includes
✔ Applying preprocessor mkdocs
✔ Making site with MkDocs
─────────────────────
Result: Hello_Foliant-0.1.0-2017-11-24.mkdocs
```

4. Run a local webserver in the site directory and see the site in your browser:

```shell
$ cd Hello_Foliant-0.1.0-2017-11-24.mkdocs
$ python -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```
