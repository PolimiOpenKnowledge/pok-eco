#!/bin/bash
set -ex

# debug version
pylint --version

coverage run --source=xapi ./manage.py test xapi
coverage report -m
coverage run --source=ecoapi ./manage.py test ecoapi
coverage report -m
coverage run --source=oai ./manage.py test oai
coverage report -m
pep8 --config=.pep8
pylint --rcfile=.pylintrc ecoapi --report=no
pylint --rcfile=.pylintrc xapi --report=no
pylint --rcfile=.pylintrc oai --report=no
