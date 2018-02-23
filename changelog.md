<<<<<<< HEAD
# 0.1.0

Initial release.

# 0.1.2

- ```foliant make gdrive``` added.

# 0.1.3

- Dependencies specified.

# 0.1.4

- Pandoc filter support added to configs.
- Pandoc failures are tracked.

# 0.1.5

- Fixed stdouting of the result document.

# 0.1.6

- Add seqdiag support.
- Add Swagger converter.
- Switch from flit to pip.

# 0.1.7

- Hotfix: Fix classifier in setup.py.

# 0.1.8

- Output file is now named according to the following format:
  `<title>_<version>-<date>`.
- You can now specify the output file name explicitly with `file_name` value
  in `config.json`. If it's not set, the slugified `title` value is used.

# 0.1.9

- Fix a false warning about `file_name` config value.

# 0.2.0

- Fix config loading on Windows.

# 0.2.1

- Add Apidoc to Markdown converter
  (via [apidoc2markdown](https://github.com/moigagoo/apidoc2markdown)).
- Markdown file converted from Swagger or Apidoc is now called `api.md`
  (instead of `swagger.md`).

# 0.2.2

- Fix non-ASCII-encoded input handling.

# 0.2.3

- Fix those pesky UTF-8 issues for good.

# 0.2.4

- ``$ pip install foliant[all]`` installs all extra requirements.

# 0.2.5

- Fix automatic versioning for non-git-based projects.

# 0.2.6

- Fix shell command execution on Linux.

# 0.2.7

- Improve output file naming: get rid of redundant "-" and "_".

# 0.2.8

- Support super advanced Markdown includes.
- Temporary directory is now called 'foliantcache' and is not
  cleaned up after build.

# 0.2.9

- Properly handle unresolved include file lookups.

# 0.3.0

- Fix remote includes without revision spec.

# 0.3.1

- Fix nested local images handling.

# 0.3.4

- Fix missing section numbers in PDF.

# 0.3.5

- Fix Gdrive upload.

# 0.3.6

- Add OpenDocument target.

# 0.3.7

- Add error reporting to seqdiag processor.
- Fix gdrive upload result output.


# 0.3.8

- Diagram files extracted from `seqdiag` blocks are now named with UUIDs, not with sequential numbers. This is done to avoid collisions during partial builds.


# 0.3.9

- GDrive upload: Upload didn't work under Docker. Fixed.
- GDrive upload: Switched from local server to command line auth.
- Docx: A warning about unkown config value "template" would pop up during build. Fixed.

# 0.4.0

- Pandoc: Added `backtick_code_blocks` option.


# 0.4.1

- Pandoc: Add support for "false" config values.
- Config: Deprecate `type` and `alt_doc_type` keys.


# 0.4.2

- Diagrams: Add PlantUML support.
- Refactor diagram processing to simplify addition of new backends.
- Add colors to output, visually improve warnings.


# 0.4.3

- Deprecate `main.yaml`.
- Add colorama to dependencies and thus fix Docker image build broken in 0.4.2.
- Remove PyYAML from dependencies.


# 0.4.4

- Make `main.yaml` deprecation softer: if `chapters` is missing in `config.json`, `main.yaml` is used instead and a warning is shown. If it's also missing, the build fails.


# 0.4.5

- Add aesthetic linebreak after the `main.yaml` warning.
- Docker: Require Ubuntu Artful to fix issue with missing title numbering due to ancient Pandoc and TeXLive versions.


# 0.4.6

- Docker: Fix EPS conversion issues.


# 0.4.7

- Remove swagger2markdown and apidoc2markdown commands. Use [swagger2markdown](https://github.com/foliant-docs/swagger2markdown) amd [apidoc2markdown](https://github.com/foliant-docs/apidoc2markdown) packages instead.
- Add `startnum` and `fancy_lists` pandoc extensions. Be aware that it'll break documents that use standard markdown enumerators which ignore list numbers themselves.
- Diagrams: Diagram sources and generated images from all backends used to sit in "diagrams" directory. Now there are subdirs for each backend.
- Includes: Unresolved include definitions are kept in the source. They used to get replaced with ''. Fixes issue #28.


# 0.4.8

- Fix PlantUML diagrams broken in 0.4.7.


# 0.4.9

- Fix Dockerfile by installing and configuring tzdata.

=======
# 1.0.0

Complete rewrite.

>>>>>>> feature/nextgen
