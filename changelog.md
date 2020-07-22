# 1.0.12

-   Add the `disable_implicit_unescape` option. Remove warning when `escape_code` is not set.
-   Support the `!env` YAML tag to use environment variables in the project config.
-   Allow to specify custom directory to store logs with the `--logs|-l` command line option.
-   Flush output to STDOUT in progress status messages and in the `foliant.utils.output()` method.
-   Get and log the names and versions of all installed Foliant-related packages.
-   Do not raise exception of the same type that is raised by a preprocessor, raise `RuntimeError` instead because some exceptions take more arguments than one.

# 1.0.11

-   Allow to specify custom options for EscapeCode preprocessor as the `escape_code.options` config parameter value.
-   Pass the `quiet` flag to `BaseParser()` as an optional argument for using in config extensions.

# 1.0.10

-   Add `escape_code` config option. To use it, escapecode and unescapecode preprocessors must be installed.

# 1.0.9

-   Process attribute values of pseudo-XML tags as YAML.
-   Allow single quotes for enclosing attribute values of pseudo-XML tags.
-   Add `!project_path` and `!rel_path` YAML tags.

# 1.0.8

-   Restore quiet mode.
-   Add the `output()` method for using in preprocessors.

# 1.0.7

-   Remove spinner made with Halo.
-   Abolish quiet mode because it is useless if extensions are allowed to write anything to STDOUT.
-   Show full tracebacks in debug mode; write full tracebacks into logs.

# 1.0.6

-   CLI: If no args are provided, print help.
-   Fix tags searching pattern in _unescape preprocessor.

# 1.0.5

-   Allow to override default config file name in CLI.
-   Allow multiline tags. Process `true` and `false` attribute values as boolean, not as integer.
-   Add tests.
-   Improve code style.

# 1.0.4

-   **Breaking change.** Add logging to all stages of building a project. Config parser extensions, CLI extensions, backends, and preprocessors can now access `self.logger` and create child loggers with `self.logger = self.logger.getChild('newbackend')`.
-   Add `pre` backend with `pre` target that applies the preprocessors from the config and returns a Foliant project that doesn't require any preprocessing.
-   `make` now returns its result, which makes is easier to call it from extensions.

# 1.0.3

-   Fix critical issue when config parsing would fail if any config value contained non-latin characters.

# 1.0.2

-   Use README.md as package description.

# 1.0.1

-   Fix critical bug with CLI module caused by missing version definition in the root `__init__.py` file.

# 1.0.0

-   Complete rewrite.
