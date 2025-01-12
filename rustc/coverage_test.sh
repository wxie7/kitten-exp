#!/bin/bash

LLVM_PROFILE_FILE="coverage/%p-%m.profraw" $RUSTC_INSTALL/bin/rustc \
  --crate-type staticlib -C link-dead-code -C debuginfo=2 -C opt-level=3 -Z mir-opt-level=3 \
  hello.rs -o hello.o

grcov coverage/*.profraw \
  -s $RUSTC_SRC/compiler \
  -b $RUSTC_INSTALL \
  --llvm-path $RUSTC_SRC/build/x86_64-unknown-linux-gnu/ci-llvm/bin \
  -t lcov -o cov.info

lcov --summary cov.info

rm -rf cov.info coverage hello.o
