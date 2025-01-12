#!/bin/bash

source env.sh

export GCOV_PREFIX_STRIP=$(echo "${GCC_BUILD}/gcc" | awk -F'/' '{print NF - 1}')
GCC_COV="/tmp/fuzz4all/gcc_1/"

cp $(pwd)/lcovrc ${HOME}/.lcovrc
cp -r ${GCC_BUILD}/gcc ${GCC_COV}
lcov -z -d ${GCC_COV}
GCOV_PREFIX=${GCC_COV} ${GCC_INSTALL}/bin/gcc -x c -std=c2x -c hello.c -o /dev/null
lcov -c -d ${GCC_COV} -o coverage.info
lcov --summary coverage.info
