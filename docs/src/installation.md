# Installation

Installing Foliant to your system can be split into three stages: installing Python with your system's package manager, installing Foliant with pip, and optionally installing Pandoc and TeXLive bundle. Below you'll find the instructions for three popular platforms: macOS, Windows, and Ubuntu.

Alternatively, you can avoid installing Foliant and its dependencies on your system by using [Docker and Docker Compose](#docker).


## macOS

1.  Install Python 3.6 with Homebrew:

        $ brew install python3

2.  Install Foliant with pip:

        $ python3 -m pip install foliant foliantcontrib.init

3.  If you plan to bake pdf or docx, install Pandoc and MacTeX with Homebrew:

        $ brew install pandoc mactex librsvg

## Windows

0.  Install [Scoop package manager](http://scoop.sh/) in PowerShell:

        $ iex (new-object net.webclient).downloadstring('https://get.scoop.sh')

1.  Install Python 3.6 with Scoop:

        $ scoop install python

2.  Install Foliant with pip:

        $ python -m pip install foliant foliantcontrib.init

3.  If you plan to bake pdf or docx, install Pandoc and MikTeX with Scoop:

        $ scoop install pandoc latex

## Ubuntu

1.  Install Python 3.6 with apt. On 14.04 and 16.04:

        $ add-apt-repository ppa:jonathonf/python-3.6
        $ apt update && apt install -y python3 python3-pip

    On newer versions:

        $ apt update && apt install -y python3 python3-pip

2.  Install Foliant with pip:

        $ python3.6 -m pip install foliant foliantcontrib.init

3.  If you plan to bake pdf or docx, install Pandoc and TeXLive with apt and wget:

        $ apt update && apt install -y wget texlive-full librsvg2-bin
        $ wget https://github.com/jgm/pandoc/releases/download/2.0.5/pandoc-2.0.5-1-amd64.deb && dpkg -i pandoc-2.0.5-1-amd64.deb

## Docker

If you use [`foliant init`](<macro mkdocs="cli/init.md" pandoc="#init">ref</macro>), `Dockerfile` and `docker-compose.yml` files to build the project are created automatically. To build the project, run:

```bash
# Site:
$ docker-compose run --rm <project-name> make site
# Pdf:
$ docker-compose run --rm <project-name> make pdf
```

Alternatively, you can create the Dockerfile manually using Foliant's official Docker images:

```docker
FROM foliant/foliant
# If you plan to bake PDFs, uncomment this line and comment the line above:
# FROM foliant/foliant:pandoc
RUN pip3 install foliantcontrib.mkdocs
```

Then, run Foliant in a container:

```bash
# Site:
$ docker run --rm -it -v `pwd`:/usr/src/app -w /usr/src/app my-project make site
# Pdf:
$ docker run --rm -it -v `pwd`:/usr/src/app -w /usr/src/app my-project make pdf
```
