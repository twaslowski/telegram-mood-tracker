#!/bin/bash

export PYTHONPATH=./
export MONGO_CONNECTION_STRING="localhost:27017"
poetry run pytest test/ --disable-warnings