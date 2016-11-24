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
