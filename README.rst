#######
Foliant
#######

**Foliant** is a documentation generator that builds PDF, Docx, and TeX
documents from Markdown source.


******
Get It
******

- Download the compiled binary from this repo's `bin` directory and use it
  right away.

- If you have Nim and Nimble installed, install foliant with Nimble:

  .. code-block:: shell

    $ nimble install foliant


*****
Usage
*****

.. code-block:: shell

  $ foliant -h

  Usage:
    foliant (build | make) <target> [--path=<project-path>]
    foliant (upload | up) <document>
    foliant (-h | --help)
    foliant --version

  Options:
    -h --help                         Show this screen.
    -v --version                      Show version.
    -p --path=<project-path>          Path to your project [default: .].


``build``, ``make``
===================

Build the output in the desired format:

- PDF. Targets: pdf, p, or anything starting with "p"
- Docx. Targets: docx, doc, d, or anything starting with "d"
- TeX. Targets: tex, t, or anything starting with "t"
- Markdown. Targets: markdown, md, m, or anything starting with "m"
- Google Drive. Targets: gdrive, google, g, or anything starting with "g"

"Google Drive" format is a shortcut for building Docx and uploading it
to Google Drive.

Specify ``--path`` if your project dir is not the current one.

Example:

.. code-block:: shell

  $ foliant make pdf


``upload``, ``up``
==================

Upload a Docx file to Google Drive as a Google document:

.. code-block:: shell

  $ foliant up MyFile.docx


**************
Project Layout
**************

For Foliant to be able to build your docs, your project must conform
to a particular layout::

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


config.json
===========

Config file, mostly for Pandoc.

.. code-block:: js

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
    "filters": ["filter1", "filter2"] // Pandoc filters
  }

For historic reasons, all config values should be strings,
even if they *mean* a number or boolean value.


main.yaml
=========

Contents file. Here, you define the order of the chapters of your project:

.. code-block:: yaml

  --- # Contents
  chapters:
  - introduction
  - chapter1
  - chapter2
  ...


references
==========

Directory with the Docx reference file. It **must** be called ``ref.docx``.


sources/
========

Directory with the Markdown source file of your project.


images/
=======

Images that can be embedded in the source files. When embedding an image,
**do not** prepend it with ``images/``:

.. code-block:: markdown

  ![](image1.png)        # RIGHT
  ![](images/image1.png) # WRONG


templates/
==========

LaTeX templates used to build PDF, Docx, and TeX files. The template
to use in build is configured in ``config.json``.


************************
Uploading to Google Drive
************************

To upload a Docx file to Google Drive as a Google document, use
``foliant upload MyFile.docx`` or `foliant build gdrive`, which is
a shortcut for generating a Docx file and uploading it.

For the upload to work, you need to have a so called *client secret* file.
Foliant looks for ``client_secrets.json`` file in the current directory.

Client secret file is obtained through Google API Console. You probably don't
need to obtain it yourself. The person who told you to use Foliant should
provide you this file as well.
