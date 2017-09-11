> Note: You can save a hell lot of time installing Foliant and its dependencies by [running it in Docker](Running-Foliant-in-Docker).

1.  Install Foliant with pip:

    ```shell
    $ pip install foliant[all]
    ```

2.  Install Pandoc and a LaTeX distrubution:

    - MacTeX for macOS with [brew](http://brew.sh/)
    - MikTeX for Windows with [scoop](http://scoop.sh/)
    - TeXLive for Linux with whater package manager you have

    > Among Linux distrubutions, Foliant was only tested on Ubuntu Xenial. See the full list of packages that must be installed in Ubuntu in the official [Foliant Dockerfile](https://github.com/foliant-docs/foliant/blob/develop/Dockerfile).

3.  Use ``foliant`` command as described in [Usage](#usage).
