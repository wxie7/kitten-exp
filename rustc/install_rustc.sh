#!/bin/bash

if [[ -z "$EXP_ROOT" || -z "$RUSTC_PREFIX" ]]; then
  echo "Please source env.sh before running this script."
  exit 1
fi

USE_LATEST=false
if [[ "$1" == "latest" ]]; then
  USE_LATEST=true
fi

if $USE_LATEST; then
  RUSTC_SRC="$RUSTC_PREFIX/test_data/rust-latest-src"
  RUSTC_INSTALL="$RUSTC_PREFIX/test_data/rust-latest-install"
fi

mkdir -p "$RUSTC_INSTALL"

if $USE_LATEST; then
  git clone --depth 1 git@github.com:rust-lang/rust.git "$RUSTC_SRC"
else
  git clone git@github.com:rust-lang/rust.git "$RUSTC_SRC"
  cd "$RUSTC_SRC"
  git checkout 788202a
fi

cd "$RUSTC_SRC"
cp config.example.toml config.toml

sed -i "432a\prefix=\"${RUSTC_INSTALL}\"" config.toml
sed -i '436a\sysconfdir="etc"' config.toml
sed -i '73a\assertions=true' config.toml
sed -i '521a\debug-assertions=true' config.toml
sed -i "365a\profiler=true" config.toml

if ! $USE_LATEST; then
  sed -i '552i\if mode != Mode::Std {\n    rustflags.arg("-Cinstrument-coverage");\n}' src/bootstrap/src/core/builder/cargo.rs
fi

./x build && ./x install
