#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pushd $SCRIPT_DIR > /dev/null
ROOT_DIR=$(git rev-parse --show-toplevel)
pushd $ROOT_DIR > /dev/null

export PYTHONPATH=$PYTHONPATH:$ROOT_DIR
. $ROOT_DIR/venv/bin/activate
python $ROOT_DIR/src/app.py

popd && popd
