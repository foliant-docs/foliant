# Docker

1.  Install [Docker](https://www.docker.com/) for your platform.

2.  Create a Dockerfile in your project directory (if you use `foliant init`, the Dockerfile is created automatically):

        FROM foliant/foliant

    If you plan to bake pdf or docx, use the image with Pandoc and TeXLive:

        FROM foliant/foliant:pandoc

    > Pandoc and TeXLive are not included in the default image because they add about 5 GB to the image size. For situations where you're interesing in site generation only, this would add way too much overhead.

3.  Build the image for your project:

        $ docker build -t my-project .

4.  Run Foliant in Docker:

        $ docker run --rm -it -v (pwd):/usr/src/app -w /usr/src/app my-project make pdf
