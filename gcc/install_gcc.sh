#!/bin/bash

if [[ -z "$EXP_ROOT" || -z "$GCC_PREFIX" ]]; then
  echo "Please source env.sh before running this script."
  exit 1
fi

USE_LATEST=false
if [[ "$1" == "latest" ]]; then
  USE_LATEST=true
fi

if $USE_LATEST; then
  GCC_VERSION="latest"
  GCC_SRC="$GCC_PREFIX/test_data/gcc-latest-src"
  GCC_INSTALL="$GCC_PREFIX/test_data/gcc-latest-install"
  GCC_BUILD="$GCC_PREFIX/test_data/gcc-latest-build"
fi

mkdir -p "$GCC_INSTALL"
mkdir -p "$GCC_BUILD"

GCC_URL="https://github.com/gcc-mirror/gcc.git"

if $USE_LATEST; then
  git clone --depth 1 $GCC_URL "$GCC_SRC"
  cd "$GCC_SRC"
else
  git clone --branch="releases/gcc-${GCC_VERSION}" $GCC_URL "$GCC_SRC"
  cd "$GCC_SRC"
fi

./contrib/download_prerequisites

cd "$GCC_BUILD"
"$GCC_SRC/configure" \
  --enable-coverage \
  --enable-checking \
  --disable-multilib \
  --disable-shared \
  --disable-bootstrap \
  --enable-languages=c,c++ \
  --prefix="$GCC_INSTALL"

make -j32 && make install
