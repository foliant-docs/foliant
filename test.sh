#!/bin/bash

# before testing make sure that you have installed the fresh version of preprocessor:
poetry install --no-interaction

# run tests
poetry lock
poetry update
poetry run pylint foliant
poetry run pytest --cov=foliant && \
poetry run codecov
