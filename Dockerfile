FROM python:latest
LABEL authors="Konstantin Molchanov <moigagoo@live.com>"

RUN apt-get update; apt-get install -y \
    xzdec \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-generic-recommended \
    texlive-lang-english \
    texlive-lang-cyrillic \
    latex-xcolor \
    texlive-math-extra \
    texlive-latex-extra \
    texlive-bibtex-extra \
    texlive-xetex \
    pandoc; \
    tlmgr init-usertree; \
    pip install foliant[all]; \
    mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENTRYPOINT ["foliant"]

ONBUILD COPY . /usr/src/app
