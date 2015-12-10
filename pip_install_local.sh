#!/bin/bash
set -ex
easy_install pip
pip install coveralls
pip install pep8
pip install pylint==1.4.4
pip install -r requirements.txt
pip install --exists-action w -r test-requirements.txt
