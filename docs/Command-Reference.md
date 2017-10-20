# Command Reference

```shell

$ foliant -h
Foliant: Markdown to PDF, Docx, ODT, and LaTeX generator powered by Pandoc.

Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document> [--secret=<client_secret*.json>]
  foliant (swagger2markdown | s2m) <swagger-location> [--output=<output-file>]
    [--template=<jinja2-template>]
  foliant (-h | --help)
  foliant --version

Options:
  -h --help                         Show this screen.
  -v --version                      Show version.
  -p --path=<project-path>          Path to your project [default: .].
  -s --secret=<client_secret*.json> Path to Google app's client secret file.
  -o --output=<output-file>         Path to the converted Markdown file
                                    [default: swagger.md]
  -t --template=<jinja2-template>   Custom Jinja2 template for the Markdown
                                    output.
```


## `build`, `make`

Build the output in the desired format:

- PDF. Targets: pdf, p, or anything starting with "p"
- Docx. Targets: docx, doc, d, or anything starting with "d"
- TeX. Targets: tex, t, or anything starting with "t"
- Markdown. Targets: markdown, md, m, or anything starting with "m"
- Google Drive. Targets: gdrive, google, g, or anything starting with "g"

"Google Drive" format is a shortcut for building Docx and uploading it
to Google Drive.

Specify `--path` if your project dir is not the current one.

Example:

```shell
$ foliant make pdf
```


## `upload`, `up`

Upload a Docx file to Google Drive as a Google document:

```shell
$ foliant up MyFile.docx
```


## `swagger2markdown`, `s2m`

Convert a [Swagger JSON](http://swagger.io/specification/) file into Markdown using [swagger2markdown](https://github.com/moigagoo/swagger2markdown).

If `--output` is not specified, the output file is called `api.md`.

Specify `--template` to provide a custom [Jinja2](http://jinja.pocoo.org/) template to customize the output. Use the [default Swagger template](https://github.com/moigagoo/swagger2markdown/blob/master/swagger.md.j2) as a reference.

Example:

```shell
$ foliant s2m http://example.com/api/swagger.json -t templates/swagger.md.j2
```


## `apidoc2markdown`, `a2m`

Convert a [Apidoc JSON](http://apidocjs.com/) files into Markdown using [apidoc2markdown](https://github.com/moigagoo/apidoc2markdown).

If `--output` is not specified, the output file is called `api.md`.

Specify `--template` to provide a custom [Jinja2](http://jinja.pocoo.org/) template to customize the output. Use the [default Apidoc template](https://github.com/moigagoo/apidoc2markdown/blob/master/apidoc.md.j2) as a reference.

Example:

```shell
$ foliant a2m /path/to/api_data.json -t templates/apidoc.md.j2
```
