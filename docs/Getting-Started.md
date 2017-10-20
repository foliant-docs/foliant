# Getting Started

1. Create your project directory from the [official cookiecutter](https://github.com/foliant-docs/cookiecutter-foliant):

   ```shell
   $ cookiecutter gh:foliant-docs/cookiecutter-foliant
   ```

2. Switch to the project directory:

   ```shell
   $ cd my-project
   ```
3. Edit the *.md files in the `sources/` directory.
4. Run Foliant from the [official Docker image](https://hub.docker.com/r/foliant/foliant/):
   ```shell
   $ docker run --rm -v `pwd`:/usr/src/app -w /usr/src/app foliant/foliant make pdf
   Collecting source... Done!
   Drawing diagrams... Done!
   Baking output... Done!
   ----
   Result: My_Project_0.1.0-26-08-2017.pdf
   ```
