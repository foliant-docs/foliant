FROM ubuntu:devel
LABEL authors="Konstantin Molchanov <moigagoo@live.com>"

ARG FOLIANT_VERSION

RUN apt-get update
RUN apt-get install -y tzdata
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-font-utils \
    texlive-generic-recommended \
    texlive-latex-recommended \
    texlive-lang-english \
    texlive-lang-cyrillic \
    texlive-fonts-extra \
    texlive-generic-extra \
    texlive-science \
    texlive-latex-extra \
    texlive-bibtex-extra \
    texlive-xetex
RUN apt-get install -y pandoc
RUN apt-get install -y git
RUN apt-get install -y plantuml
RUN apt-get install -y python3 python3-pip
RUN pip3 install "foliant[all]>=$FOLIANT_VERSION"
RUN apt-get install locales && locale-gen en_US.UTF-8

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

ENTRYPOINT ["foliant"]
