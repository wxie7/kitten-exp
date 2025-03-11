#!/bin/bash

# export EXP_ROOT=$(cd "$(dirname "$(realpath "$0")")" && pwd)
export EXP_ROOT=$(pwd)

# export OPENAI_API_KEY=""
# export OPENAI_API_URL=""

export TMPDIR="$EXP_ROOT/temp"
mkdir -p $TMPDIR

# For GCC
export GCC_PREFIX=$EXP_ROOT/gcc
export GCC_VERSION="13.1.0"

export GCC_SRC="$GCC_PREFIX/test_data/gcc-${GCC_VERSION}-src"
export GCC_INSTALL="$GCC_PREFIX/test_data/gcc-${GCC_VERSION}-install"
export GCC_BUILD="$GCC_PREFIX/test_data/gcc-${GCC_VERSION}-build"
export GCC_SEEDS="$GCC_PREFIX/test_data/gcc-${GCC_VERSION}-seeds"

# For RUSTC
export RUSTC_PREFIX=$EXP_ROOT/rustc
export RUSTC_VERSION="788202a"

export RUSTC_SRC="$RUSTC_PREFIX/test_data/rust-${RUSTC_VERSION}-src"
export RUSTC_INSTALL="$RUSTC_PREFIX/test_data/rustc-${RUSTC_VERSION}-install"
export RUSTC_SEEDS="$RUSTC_PREFIX/test_data/rustc-${RUSTC_VERSION}-seeds"

export LLVM_VERSION="19.1.6"
export LLVM_PREFIX="$EXP_ROOT/llvm"

export LLVM_SRC="$LLVM_PREFIX/test_data/llvm-${LLVM_VERSION}-src"
export LLVM_INSTALL="$LLVM_PREFIX/test_data/llvm-${LLVM_VERSION}-install"
export LLVM_BUILD="$LLVM_PREFIX/test_data/llvm-${LLVM_VERSION}-build"
export LLVM_SEEDS="$LLVM_PREFIX/test_data/llvm-${LLVM_VERSION}-seeds"
