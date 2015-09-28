#!/bin/bash
set -ex

coverage run --source=oai,ecoapi,xapi ./manage.py test xapi
coverage run --source=oai,ecoapi,xapi ./manage.py test ecoapi
coverage run --source=oai,ecoapi,xapi ./manage.py test oai
coverage report -m
pep8 --config=.pep8 oai
pylint --rcfile=.pylintrc oai --report=no
pep8 --config=.pep8 ecoapi
pylint --rcfile=.pylintrc ecoapi --report=no
pep8 --config=.pep8 xapi
pylint --rcfile=.pylintrc xapi --report=no
