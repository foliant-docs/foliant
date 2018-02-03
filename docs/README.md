#   Foliant Documentation

##  Build Locally

With Docker Compose:

```bash
$ git clone git@github.com:foliant-docs/foliant.git
$ cd foliant/docs
# Site:
$ docker-compose run --rm foliant-docs make site
# PDF:
$ docker-compose run --rm foliant-docs make pdf
```

With pip and stuff (requires Python 3.6+, Pandoc, and TeXLive):

```bash
$ git clone git@github.com:foliant-docs/foliant.git
$ cd foliant/docs
$ pip install -r requirements
# Site:
$ foliant make site
# PDF:
$ foliant make pdf
```
