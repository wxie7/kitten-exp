#!/bin/bash

set -x

if [[ -z "$EXP_ROOT" || -z "$GCC_PREFIX" ]]; then
  echo "Please source env.sh before running this script."
  exit 1
fi

USE_LATEST=false
if [[ "$1" == "latest" ]]; then
  USE_LATEST=true
fi

if $USE_LATEST; then
  LLVM_VERSION="latest"
  LLVM_SRC="$LLVM_PREFIX/test_data/llvm-latest-src"
  LLVM_INSTALL="$LLVM_PREFIX/test_data/llvm-latest-install"
  LLVM_BUILD="$LLVM_PREFIX/test_data/llvm-latest-build"
fi

mkdir -p $LLVM_PREFIX/test_data
cd $LLVM_PREFIX/test_data

if $USE_LATEST; then
  git clone --depth 1 git@github.com:llvm/llvm-project.git $LLVM_SRC
else
  wget https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-${LLVM_VERSION}.tar.gz
  tar xf llvmorg-${LLVM_VERSION}.tar.gz
  mv llvm-project-llvmorg-${LLVM_VERSION} $LLVM_SRC
fi

cd $LLVM_SRC

if $USE_LATEST; then
  cmake -GNinja -DLLVM_ENABLE_PROJECTS="clang" \
    -DCMAKE_BUILD_TYPE=Release \
    -B$LLVM_BUILD -Sllvm \
    -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -DCMAKE_INSTALL_PREFIX=$LLVM_INSTALL
else
  cmake -GNinja -DLLVM_ENABLE_PROJECTS="clang" \
    -DCMAKE_BUILD_TYPE=Release \
    -B$LLVM_BUILD -Sllvm \
    -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -DLLVM_BUILD_INSTRUMENTED_COVERAGE=ON \
    -DCMAKE_INSTALL_PREFIX=$LLVM_INSTALL
fi

cmake --build $LLVM_BUILD && cmake --install $LLVM_BUILD
