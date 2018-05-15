# 1.0.0

-   Complete rewrite.

# 1.0.1

-   Fix critical bug with CLI module caused by missing version definition in the root `__init__.py` file.

# 1.0.2

-   Use README.md as package description.


# 1.0.3

-   Fix critical issue when config parsing would fail if any config value contained non-latin characters.


# 1.0.4

-   **Breaking change.** Add logging to all stages of building a project. Config parser extensions, CLI extensions, backends, and preprocessors can now access `self.logger` and create child loggers with `self.logger = self.logger.getChild('newbackend')`.
-   Add `pre` backend with `pre` target that applies the preprocessors from the config and returns a Foliant project that doesn't require any preprocessing.
-   `make` now returns its result, which makes is easier to call it from extensions.


# 1.0.5

-   Allow to override default config file name in CLI.
