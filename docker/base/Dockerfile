# start with a base image
FROM ubuntu:12.04
MAINTAINER Marco Re <mrc.re@tiscali.it>

ENV DJANGO_SETTINGS_MODULE="test-settings"
ENV BUILD_DIR="/src"

# install dependencies
RUN apt-get update
RUN apt-get install -y \
  build-essential \
  git \
  python \
  python-pip \
  libmysqlclient-dev \
  python-dev \
  swig \
  libxml2-dev \
  libxslt1-dev \
  libxmlsec1-dev \
  libfreetype6-dev \
  python-pip \
  python-apt \
  python-dev \
  graphviz \
  libgraphviz-dev \
  graphviz-dev \
  pkg-config \
  gfortran \
  libopenblas-dev \
  liblapack-dev \
  libgeos-dev \
  libffi6 \
  libffi-dev \
  libtiff4-dev libjpeg8-dev zlib1g-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
