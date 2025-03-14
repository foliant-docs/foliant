#!/bin/bash

# before testing make sure that you have installed the fresh version of preprocessor:
poetry install --no-interaction

# run tests
poetry run pytest --cov=foliant -v
