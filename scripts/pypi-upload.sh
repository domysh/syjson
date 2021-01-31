#!/bin/bash

/bin/bash clear.sh

cd "$(dirname "$0")"
cd ..

python3 setup.py sdist
twine upload dist/*
