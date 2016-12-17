**Foliant** is a documentation generator that builds PDF, Docx, and TeX documents from Markdown source.

- [Home](https://github.com/foliant-docs/foliant/)
- [Issues](https://github.com/foliant-docs/foliant/issues)
- [User's manual](https://github.com/foliant-docs/foliant/#usage)
- [Troubleshooting](https://github.com/foliant-docs/foliant/#troubleshooting)


# How to Use This Repo

1.  In your project directory, create a file called `Dockerfile` with the following content:

    ```dockerfile
    FROM foliant/foliant

    # If necessary, add fonts and install additional packages:
    # RUN apt-get install wget; \
    #     wget http://www.paratype.ru/uni/public/PTSans.zip; \
    #     mkdir -p /usr/share/fonts/truetype/ptsans/; \
    #     unzip PTSans.zip -d /usr/share/fonts/truetype/ptsans/; \
    #     rm PTSans.zip; \
    #     fc-cache -fv
    RUN mkdir -p /usr/src/app

    WORKDIR /usr/src/app
    ```

2.  In your project directory, create a file called `docker-compose.yml` with the following content:

    ```yaml
    my-foliant-project:
      build: .
      volumes:
          - .:/usr/src/app
    ```

3.  Build your project's image and run a container with the same params as the [regular ``foliant`` command](https://github.com/foliant-docs/foliant/#usage).

    For example, build PDF:

    ```shell
    $ docker-compose run --rm my-foliant-project make pdf
    Collecting source... Done!
    Drawing diagrams... Done!
    Baking output... Done!
    ----
    Result: Dolor_sit_amet_16-12-2016.pdf
    ```

**Warning:** *Uploading to Google Drive currently doesn't work if you run Foliant in a container.*
