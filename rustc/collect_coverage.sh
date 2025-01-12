#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <left> <right>"
  exit 1
fi

left=$1
right=$2

for ((i = left; i <= right; i++)); do
  grcov "$TEMP_DIR/rust_$i" -s "$RUSTC_SRC/compiler" -b "$RUSTC_INSTALL" \
    --llvm-path "$RUSTC_SRC/build/x86_64-unknown-linux-gnu/ci-llvm/bin" \
    -t lcov -o "cov_rustc_${i}.info"

  if [ -f "cov_rustc_$((i - 1)).info" ]; then
    lcov -a "cov_rustc_$((i - 1)).info" -a "cov_rustc_${i}.info" -o "cov_rustc_${i}.info"
  fi
done
