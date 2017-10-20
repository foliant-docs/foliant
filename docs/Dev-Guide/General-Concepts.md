# General Concepts

## Git

Foliant is developed with git, the code is hosted on GitHub.

We follow git flow methodology: all development happens in feature branches and "develop" branch.

Foreign code contributions are submitted as pull requests, reviewed by a member of the team, and merged into "develop."

Commits *never* go directly into "master," only merge commits during releases do.


## Python

Foliant supports Python 3.5+. We do *not* support legacy Python.


## OSes

Foliant is guaranteed to run on Windows, macOS, and Ubuntu. Other GNU/Linux distros should also work, but none was tested.


## Dependencies

Foliant requires [Pandoc](http://pandoc.org/) and LaTeX. Depending on the OS, you'll need either MikTeX, MacTeX, or TeXLive.

On Windows, the recommended way to install the dependencies is with [scoop](http://scoop.sh):

```shell
$ scoop install pandoc latex
```

During the first run, you'll be prompted to install missing LaTeX packages.

On macOS, use [brew](https://brew.sh/) to install Pandoc:

```shell
$ brew install pandoc
```

and [MacTeX installer](https://www.tug.org/mactex/) for MacTeX.

You'll have to install LaTeX packages manually.

On Ubuntu, for the list of recommended packages, refer to the [official Docker image](https://github.com/foliant-docs/foliant/blob/develop/Dockerfile#L6-L23).
