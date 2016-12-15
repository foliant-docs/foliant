FROM foliant/foliant:latest

RUN apt-get install wget; \
    mkdir -p /usr/share/fonts/truetype/ptsans/; \
    wget http://www.paratype.ru/uni/public/PTSans.zip; \
    unzip PTSans.zip -d /usr/share/fonts/truetype/ptsans/; \
    rm PTSans.zip; \
    fc-cache -fv
