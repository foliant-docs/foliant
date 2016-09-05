# Foliant

**Foliant** is a documentation generator that builds PDF, Docx, and TeX
documents from Markdown source.

# Get It

From PyPI:

```shell
$ pip install foliant
```

# Usage

```
Usage:
  foliant (build | make) <target> [--path=<project-path>]
  foliant (upload | up) <document>
  foliant (-h | --help)
  foliant --version
```

# Project Layout

For foliant to be able to build your docs, your project must conform
to a particular layout:

```
.
│   config.json
│   main.yaml
│
├───references
│       ref.docx
│
├───sources
│   │   chapter1.md
│   │   introduction.md
│   │
│   └───images
│           Lenna.png
│
└───templates
        basic.tex
        restream_logo.png
```

## config.json

Config file, mostly for Pandoc.

```js
{
  "title": "Lorem ipsum",           // Document title.
  "second_title": "Dolor sit amet", // Document subtitle.
  "lang": "english",                // Document language, "russian" or "english."
                                    // If not specified, "russian" is used.
  "company": "restream",            // Your company name, "undev" or "restream".
                                    // Shown at the bottom of each page.
  "year": "2016",                   // Document publication year.
                                    // Shown at the bottom of each page.
  "title_page": "true",             // Add title page or not.
  "toc": "true",                    // Add table of contents or not.
  "tof": "true",                    // Unknown
  "template": "basic",              // LaTeX template to use. Do NOT add ".tex"!
  "version": "1.0",                 // Document version. If not specified
                                    // or set to "auto," the version is generated
                                    // automatically based on git tag and revision number.
  "date":"true",                    // Add date to the title page.
  "type": "",                       // Unknown
  "alt_doc_type": "",               // Unknown
}
```

For historic reasons, all config values should be strings,
even if they *mean* a number or boolean value.

## main.yaml

Contents file. Here, you define the order of the chapters of your project:

```yaml
--- # Contents
chapters:
- introduction
- chapter1
- chapter2
...
```

## references/

Directory with the Docx reference file. It **must** be called `ref.docx`.

## sources/

Directory with the Markdown source file of your project.

## images/

Images that can be embedded in the source files. When embedding an image,
**do not** prepend it with `images/`:

```markdown
![](image1.png)        # RIGHT
![](images/image1.png) # WRONG
```
## templates/

LaTeX templates used to build PDF, Docx, and TeX files. The template
to use in build is configured in `config.json`.

# Uploading to Google Drive

To upload a Docx file to Google Drive as a Google Docs document, use
`foliant upload` command or `foliant build --target=gdrive`, which is
a shortcut for generating a Docx file and uploading it.

For the upload to work, you need to have a so called *client secret* file
in the directory it was invoked in.

Client secret file is obtained through Google API Console. You probably don't
need to obtain it yourself. The person who told you to use foliant should
provide you this file as well.
