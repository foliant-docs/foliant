FROM foliant/foliant:pandoc

COPY requirements.txt .
COPY template template

RUN pip3 install -r requirements.txt
RUN mkdir -p /usr/share/fonts/truetype/ptsans; \
    mkdir -p /usr/share/fonts/truetype/ptmono; \
    unzip template/PTSans.zip -d /usr/share/fonts/truetype/ptsans; \
    unzip template/PTMono.zip -d /usr/share/fonts/truetype/ptmono; \
    fc-cache -fv
