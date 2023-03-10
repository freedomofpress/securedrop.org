#!/bin/bash

# This script constructs requirements.txt and dev-requirements.txt
# from requirements.in and dev-requirements.in, respectively.
# Intended to be run during the docker build process for the Django
# image.

set -e

pip-compile --generate-hashes --no-header --allow-unsafe --resolver=backtracking --output-file requirements.txt requirements.in

pip-compile --generate-hashes --no-header --allow-unsafe --resolver=backtracking --output-file dev-requirements.txt dev-requirements.in
