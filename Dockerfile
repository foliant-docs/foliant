FROM ubuntu:latest
LABEL authors="Konstantin Molchanov <moigagoo@live.com>"

RUN apt-get update; apt-get install -y \
    python3 python3-pip \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-generic-recommended \
    texlive-lang-english \
    texlive-lang-cyrillic \
    latex-xcolor \
    texlive-fonts-extra \
    texlive-generic-extra \
    texlive-math-extra \
    texlive-latex-extra \
    texlive-bibtex-extra \
    texlive-xetex \
    pandoc; \
    mkdir -p /usr/src/app
RUN pip3 install "foliant[all]>=0.2.7"
WORKDIR /usr/src/app
ENTRYPOINT ["foliant"]

ONBUILD COPY . /usr/src/app