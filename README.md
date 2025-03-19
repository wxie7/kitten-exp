# Kitten Experiment

## 1. Preparation

Before running this experiment, follow these steps:

1. **Load environment variables**  
```bash
source env.sh
```
2. **Install GCC LLVM and Rustc**
```bash
bash gcc/install_gcc.sh
bash rustc/install_llvm.sh
bash rustc/install_rustc.sh
```
3. **(Optional)Install the latest versions of GCC LLVM and Rustc**
```bash
bash gcc/install_gcc.sh latest
bash gcc/install_llvm.sh latest
bash rustc/install_rustc.sh latest
```
4. **Compile Kitten**
```bash
git clone https://github.com/uw-pluverse/perses.git
bazel build kitten/src/org/perses/fuzzer:kitten_deploy.jar
cp bazel-bin/kitten/src/org/perses/fuzzer/kitten_deploy.jar $EXP_ROOT
```
5. **Collect seeds for C and Rust**  
```bash
cd $EXP_ROOT
python3 gcc/copy_seeds.py
python3 rustc/copy_seeds.py
```

## 2. Run Kitten

**Kitten Usage**  
You can view instructions for using Kitten by running:
```bash
java -jar $EXP_ROOT/kitten_deploy.jar --help
```
Or by visiting [Kitten](https://github.com/uw-pluverse/perses/tree/master/kitten).

**Test Gcc**
```bash
cd $EXP_ROOT
bash kitten/gcc/fullrun.sh
cd $EXP_ROOT/kitten/gcc/fullrun/coverage
python3 $EXP_ROOT/kitten/merge_coverage_to_csv.py 1 24 lines.csv
```
**Test LLVM**
```bash
cd $EXP_ROOT
bash kitten/llvm/fullrun.sh
cd $EXP_ROOT/kitten/llvm/fullrun/coverage
python3 $EXP_ROOT/kitten/merge_coverage_to_csv.py 1 24 lines.csv
```
**Test Rustc**
```bash
cd $EXP_ROOT
bash kitten/rustc/fullrun.sh
cd $EXP_ROOT/kitten/rustc/fullrun/coverage
python3 $EXP_ROOT/kitten/merge_coverage_to_csv.py 1 24 lines.csv
```
> The bug file is located in the default_finding_folder of fullrun

## 3. (Optional) Compare to fuzz4all

```bash
cd $EXP_ROOT
git clone https://github.com/wxie7/fuzz4all.git
# Complete the environment configuration according to https://github.com/fuzz4all/fuzz4all
```

**Test GCC/LLVM**
```bash
cd $EXP_ROOT/fuzz4all
python3 Fuzz4All/fuzz.py --config config/full_run/c_std.yaml main_with_config --target $GCC_INSTALL/bin/gcc --model_name bigcode/starcoderbase --folder Results/Gcc
python3 collect_gcc_coverage.py
# LLVM
# python3 Fuzz4All/fuzz.py --config config/full_run/c_std.yaml main_with_config --target $LLVM_INSTALL/bin/clang --model_name bigcode/starcoderbase --folder Results/LLVM
```

**Test Rustc**
```bash
cd $EXP_ROOT/fuzz4all
python3 Fuzz4All/fuzz.py --config config/full_run/rust.yaml main_with_config --target $RUSTC_INSTALL/bin/rustc --model_name bigcode/starcoderbase --folder Results/Rust
python3 collect_rustc_coverage.py
```