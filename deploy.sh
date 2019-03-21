#!/bin/sh

deploy_to_pypi() {
  echo "Building distribution"
  python setup.py sdist bdist_wheel
  echo "Pushing new version to PyPi"
  twine upload dist/* -u $PYPI_USERNAME -p $PYPI_PASSWORD 
}

build_docs() {
  echo "Building documentation files"
  sphinx-apidoc -f -e -d 4 -o ./docs ./honeybee
  sphinx-build -b html ./docs ./docs/_build/docs -D release=$1 -D version=$1
}


if [ -n "$1" ]
then
  NEXT_RELEASE_VERSION=$1
else
  echo "A release version must be supplied"
  exit 1
fi

deploy_to_pypi
build_docs $NEXT_RELEASE_VERSION