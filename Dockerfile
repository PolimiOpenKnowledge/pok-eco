# Use as base image the image builded with Dockerfile_localreqs. This is essentially done to use docker caching layer
FROM marcore/pok_eco_local
MAINTAINER Marco Re <mrc.re@tiscali.it>

ENV PYTHONENV="/src"
# specify working directory
WORKDIR /src

# copy edx deps
RUN /src/copy_edx_dependencies.sh

# grab contents of source directory
ADD . /src/

RUN /src/pip_install_local.sh

CMD /src/run_tests.sh
