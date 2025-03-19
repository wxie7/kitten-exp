#!/usr/bin/env bash

set -o pipefail
set -o nounset
set -o errexit

if [[ -z "$EXP_ROOT" || -z "$GCC_PREFIX" ]]; then
  echo "Please source env.sh before running this script."
  exit 1
fi

cd $EXP_ROOT
readonly CAMPAIGN_ROOT_DIR="kitten/rustc/fuzz4all-seeds"

readonly FINDING_FOLDER="${CAMPAIGN_ROOT_DIR}/default_finding_folder"
readonly MUTANTS_FOLDER="${CAMPAIGN_ROOT_DIR}/default_mutants_folder"
readonly TEMP_FOLDER="${CAMPAIGN_ROOT_DIR}/default_temp_folder"
readonly LOG_FILE="${CAMPAIGN_ROOT_DIR}/testing-process.log"
readonly COVERAGE_SAVE="${CAMPAIGN_ROOT_DIR}/coverage"
readonly KITTEN_TIMEOUT=86400

mkdir -p "${CAMPAIGN_ROOT_DIR}"
mkdir -p "${FINDING_FOLDER}"
mkdir -p "${MUTANTS_FOLDER}"
mkdir -p "${TEMP_FOLDER}"
mkdir -p "${COVERAGE_SAVE}"

java -Xmx210G -Xms30G -jar $EXP_ROOT/kitten_deploy.jar \
  --testing-config "$EXP_ROOT/kitten/rustc/fuzz4all-seeds-config.yaml" \
  --random-seed 0 \
  --seed-limit 10000 \
  --timeout ${KITTEN_TIMEOUT} \
  --max-recursions 5 \
  --enable-splicing true \
  --generator "RANDOM_GENERATOR" \
  --enable-deleting-on-random-positions true \
  --enable-deleting-on-continuous-positions true \
  --enable-inserting-on-random-positions true \
  --enable-inserting-on-continuous-positions true \
  --enable-replacing-on-random-positions true \
  --enable-replacing-on-continuous-positions true \
  --enable-replacing-identifier true \
  --enable-replacing-same-type-token true \
  --threads 1 \
  --verbosity "INFO" \
  --fuzzer-mode NORMAL_FUZZING \
  --mutants-folder ${MUTANTS_FOLDER} \
  --finding-folder ${FINDING_FOLDER} \
  --temp-folder ${TEMP_FOLDER} \
  --rustc-coverage-mode true \
  --coverage-interval 3600 \
  --coverage-timeout ${KITTEN_TIMEOUT} \
  --coverage-save ${COVERAGE_SAVE} \
  --compiler-source ${RUSTC_SRC}/compiler \
  --compiler-binary ${RUSTC_INSTALL} \
  --llvm-path $RUSTC_SRC/build/x86_64-unknown-linux-gnu/ci-llvm/bin \
  2>&1 | tee "${LOG_FILE}"
