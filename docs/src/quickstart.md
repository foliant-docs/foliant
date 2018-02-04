# Quickstart

In this tutorial, you'll learn how to use Foliant to build websites and pdf documents from a single Markdown source. You'll also learn how to use Foliant preprocessors.


## Create New Project

All Foliant projects must adhere to a certain structure. Luckily, you don't have to memorize it thanks to [Init](<macro pandoc="#foliantcontrib-init" mkdocs="cli/init.md">ref</macro>) extension.

You should have installed it during [Foliant installation](<macro pandoc="#installation" mkdocs="installation.md">ref</macro>) and it's included in Foliant's default Docker image.

```bash
$ foliant init
Enter the project name: Hello Foliant
✔ Generating Foliant project
─────────────────────
Project "Hello Foliant" created in path/to/hello-foliant
$ cd hello-foliant
$ tree
.
├── foliant.yml
└── src
    └── index.md

1 directory, 2 files
```

To do the same with Docker, run:

```bash
$ docker run --rm -it -v `pwd`:/usr/app/src -w /usr/app/src foliant/foliant init
Enter the project name: Hello Foliant
✔ Generating Foliant project
─────────────────────
Project "Hello Foliant" created in /usr/app/src/hello-foliant
```

Init command created a config file `foliant.yml` and a source directory `src` with one source file `index.md`. And that is the simplest Foliant project!


## Build Site

In the project directory, run:

```bash
$ foliant make site
✔ Parsing config
✔ Applying preprocessor mkdocs
✔ Making site with MkDocs
─────────────────────
Result: Hello_Foliant-2018-01-23.mkdocs
```

Or, with Docker Compose:

```bash
$ docker-compose run --rm hello-foliant make site
✔ Parsing config
✔ Applying preprocessor mkdocs
✔ Making site with MkDocs
─────────────────────
Result: Hello_Foliant-2018-01-23.mkdocs
```


That's it! Your static, MkDocs-powered website is ready. To view it, use any web server, for example, Python's built-in one:

```bash
$ cd Hello_Foliant-2018-01-23.mkdocs
$ python -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

Open [localhost:8000](http://localhost:8000) in your web browser. You should see something like this:

![Basic Foliant project build with MkDocs](_img/basic-mkdocs.png)


## Build Pdf

>   **Note**
>
>   To build pdfs with Pandoc, make sure you have it and TeXLive installed (see [Installation](<macro pandoc="#installation" mkdocs="installation.md">ref</macro>)).

In the project directory, run:

```bash
$ foliant make pdf
✔ Parsing config
✔ Applying preprocessor flatten
✔ Making pdf with Pandoc
─────────────────────
Result: Hello_Foliant-2018-01-23.pdf
```

If you want to build pdf with Docker, make sure you use `foliant/foliant:pandoc` as your base image, i.e. that your `Dockerfile` starts with:

```docker
FROM foliant/foliant:pandoc
```

Then, run this command in the project directory:

```bash
$ docker-compose run --rm hello-foliant make pdf
✔ Parsing config
✔ Applying preprocessor flatten
✔ Making pdf with Pandoc
─────────────────────
Result: Hello_Foliant-2018-01-23.pdf
```

Your standalone pdf documentation is ready! Open it with your favorite pdf viewer and you should see something like this:

![Basic Foliant project build with MkDocs](_img/basic-pdf.png)
