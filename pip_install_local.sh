#!/bin/bash
set -ex
easy_install pip
pip install coveralls
pip install pep8
pip install -r requirements.txt
pip install -r test-requirements.txt
