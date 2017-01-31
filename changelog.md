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

# 0.2.9

- Properly handle unresolved include file lookups.
