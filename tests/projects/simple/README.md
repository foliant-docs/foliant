#   Pre Backend Test Project

##  Build Instructions

With Docker Compose:

```bash
# Site:
$ docker-compose run --rm pre-backend-test-project make site
# PDF:
$ docker-compose run --rm pre-backend-test-project make pdf
```

With pip and stuff (requires Python 3.6+, Pandoc, and TeXLive):

```bash
$ pip install -r requirements.txt
# Site:
$ foliant make site
# PDF:
$ foliant make pdf
```
