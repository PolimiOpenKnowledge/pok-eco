#!/bin/bash
set -ex

pip install coveralls
pip install pep8
pip install pylint
pip install -r requirements.txt
pip install -r test-requirements.txt
