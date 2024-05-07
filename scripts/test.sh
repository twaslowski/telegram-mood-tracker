#!/bin/bash

set -e

echo "launching localstack container"
docker run -d --rm --name localstack -p 4566:4566 -p 4571:4571 localstack/localstack

echo "waiting for localstack to be ready"
sleep 3

echo "running tests"
if [ -d .venv ]; then
  echo "found existing virtual environment. activating ..."
  source .venv/bin/activate
else
  echo "no virtual environment found. assuming dependencies are available."
fi

export AWS_ACCESS_KEY_ID=foo
export AWS_SECRET_ACCESS_KEY=bar

export PYTHONPATH=./ && poetry run coverage run -m pytest
poetry run coverage xml -o test/coverage.xml
poetry run coverage-badge -f -o test/coverage.svg

echo "cleaning up"
docker stop localstack
