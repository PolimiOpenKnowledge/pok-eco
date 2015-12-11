#!/bin/bash
set -ex


copyEdxApp()
{
  mkdir "$BUILD_DIR/$1"
  cp -r "$PYTHONENV"/src/edx-platform/$2/djangoapps/$1/* "${BUILD_DIR}/$1/"
}

installEdxRequirements()
{
  echo "Installing edx-platform requirements $1 .."
  pip install $2 -r requirements/edx/$1
  echo "..done"
}

copyEdxApp track common
copyEdxApp xmodule_django common
copyEdxApp edxmako common
copyEdxApp course_modes common
copyEdxApp config_models common
copyEdxApp util common
copyEdxApp static_replace common
copyEdxApp request_cache common
copyEdxApp external_auth common
copyEdxApp third_party_auth common
copyEdxApp student common
copyEdxApp xblock_django common
copyEdxApp microsite_configuration common
copyEdxApp certificates lms
copyEdxApp branding lms
copyEdxApp courseware lms
copyEdxApp psychometrics lms
copyEdxApp verify_student lms

cd "$PYTHONENV/src/edx-platform"
installEdxRequirements pre.txt
installEdxRequirements base.txt
installEdxRequirements github.txt "--exists-action w"
installEdxRequirements local.txt
pip install -e --upgrade git+https://github.com/edx/edx-lint.git@v0.3.2#egg=edx_lint==0.3.2

mkdir "$BUILD_DIR/test_root"
cp -r "$PYTHONENV"/src/edx-platform/test_root/* "${BUILD_DIR}/test_root/"
