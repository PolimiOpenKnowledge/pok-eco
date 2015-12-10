#!/bin/bash
set -ex
easy_install pip
pip install coveralls
pip install pep8
pip install pylint
pip install --exists-action w -r requirements.txt
pip install --exists-action w -r test-requirements.txt
