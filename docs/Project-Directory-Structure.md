# Project Directory Structure

For Foliant to be able to build your docs, your project must conform to a particular layout:

    .
    │   config.json
    │
    ├───references
    │       ref.docx
    │       ref.odt
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
            company_logo.png

> **Important**
>
> After ``foliant make`` is invoked, a directory called ``foliantcache`` is created in the directory where you run Foliant. The ``foliantcache`` directory stores temporary files and included repos.
>
> The ``foliantcache`` directory should not be tracked by your version control system, because it will double your repo size at best. Add ``foliantcache`` to ``.gitignore`` or ``.hgignore``.


## config.json

Config file, mostly for Pandoc.

```js

{
    "title": "Lorem ipsum",           // Document title.
    "file_name": "Dolor_sit_amet",    // Output file name. If not set, slugified
                                      // `title` is used.
    "second_title": "Dolor sit amet", // Document subtitle.
    "chapters":[                      // Chapters of your project in the order they
        "intro",                      // will appear in the document. Each entry
        "chapter1"                    // corresponds to a .md file in "sources" dir.
    ]
    "lang": "english",                // Document language, "russian" or "english."
                                      // If not specified, "russian" is used.
    "company": "My Company",          // Your company name to fill in latex template.
                                      // Shown at the bottom of each page.
    "year": "2016",                   // Document publication year.
                                      // Shown at the bottom of each page.
    "title_page": "true",             // Add title page or not.
    "toc": "true",                    // Add table of contents or not.
    "tof": "true",                    // Add table of figures or not.
    "template": "basic",              // LaTeX template to use. Do NOT add ".tex"!
    "version": "1.0",                 // Document version. If set to "auto"
                                      // the version is generated automatically
                                      // based on git tag and revision number in master.
    "date": "true",                   // Add date to the title page and output
                                      // file name.
    "filters": ["filter1", "filter2"] // Pandoc filters.
    "git": {                          // Git aliases for includes.
    "foliant": "git@github.com:foliant-docs/foliant.git" // Git alias.
    }
}
```

For historic reasons, all config values should be strings, even if they *mean* a number or boolean value.


## main.yaml

> Important! `main.yaml` is deprecated since 0.4.3. Use `chapters` key in `config.json` instead. 

Contents file. Here, you define the order of the chapters of your project:

```yaml
chapters:
    - introduction
    - chapter1
    - chapter2
```


## references/

Directory with the Docx and ODT reference files. They **must** be called `ref.docx` and `ref.odt`.


## sources/

Directory with the Markdown source file of your project.


## sources/images/

Images that can be embedded in the source files. When embedding an image, **do not** prepend it with `images/`:

```markdown
![](image1.png)        # right
![](images/image1.png) # wrong
```


## templates/

LaTeX templates used to build PDF, Docx, and TeX files. The template to use in build is configured in `config.json`.
