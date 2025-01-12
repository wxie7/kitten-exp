import os
import subprocess
from tqdm import tqdm
import shutil

# Constants
RUSTC_INSTALL = os.getenv("RUSTC_INSTALL")
RUSTC_SRC = os.getenv("RUSTC_SRC")
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/fuzz4all/rustc")
if not RUSTC_INSTALL:
    print("RUSTC_INSTALL environment variable not set.")
    exit(1)
if not RUSTC_SRC:
    print("RUSTC_SRC environment variable not set.")
    exit(1)

os.makedirs(TEMP_DIR, exist_ok=True)

RUSTC_TESTS_DIR = os.path.join(RUSTC_SRC, "tests")
if not os.path.isdir(RUSTC_TESTS_DIR):
    print(f"{RUSTC_TESTS_DIR} directory does not exist.")
    exit(1)

RUSTC_COMMAND = os.path.join(RUSTC_INSTALL, "bin", "rustc")
COMPILE_ARGS = [
    "--crate-type", "staticlib",
    "-C", "link-dead-code",
    "-C", "debuginfo=2",
    "-C", "opt-level=3",
    "-Z", "mir-opt-level=3"
]
TIMEOUT = 30

# Set LLVM_PROFILE_FILE to prevent profraw files from being generated
os.environ["LLVM_PROFILE_FILE"] = "/dev/null"

def main():
    objects_dir = os.path.join(TEMP_DIR, "objects")
    os.makedirs(objects_dir, exist_ok=True)

    rustc_seeds = os.getenv("RUSTC_SEEDS")
    if not rustc_seeds:
        print("RUSTC_SEEDS environment variable not set.")
        return
    os.makedirs(rustc_seeds, exist_ok=True)

    # Scan for .rs files in tests directory
    rs_files = []
    for dirpath, _, filenames in os.walk(RUSTC_TESTS_DIR):
        for file in filenames:
            if file.endswith(".rs"):
                rs_files.append(os.path.join(dirpath, file))

    ice_count = 0
    timeout_count = 0

    progress_bar = tqdm(rs_files, desc="Compiling .rs files", unit="file")
    for rs_file in progress_bar:
        file_name = os.path.basename(rs_file).replace(".rs", "")
        output_file = os.path.join(objects_dir, f"{file_name}.o")
        cmd = [
            "timeout", str(TIMEOUT), RUSTC_COMMAND,
            *COMPILE_ARGS, rs_file,
            "-o", output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 124:  # Timeout
            timeout_count += 1
            progress_bar.set_postfix(ICE=ice_count, Timeout=timeout_count)
            print(f"Timeout: {rs_file}")
        elif "internal compiler error" in result.stderr or "'rustc' panicked" in result.stderr:
            ice_count += 1
            progress_bar.set_postfix(ICE=ice_count, Timeout=timeout_count)
            print(f"ICE: {rs_file}")
        else:
            # Move to RUSTC_SEEDS directory for "other cases"
            target_path = os.path.join(rustc_seeds, os.path.basename(rs_file))
            shutil.copy(rs_file, target_path)

    print(f"Compilation completed. ICE: {ice_count}, Timeouts: {timeout_count}")

if __name__ == "__main__":
    main()

