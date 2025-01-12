import os
import subprocess
from pathlib import Path
import shutil
from datetime import datetime, timedelta
from tqdm import tqdm

# Get GCC path and build directory from environment variables
GCC_INSTALL = os.getenv("GCC_INSTALL")
GCC_BUILD = os.getenv("GCC_BUILD")
EXP_ROOT = os.getenv("EXP_ROOT")

if not GCC_INSTALL or not os.path.isfile(os.path.join(GCC_INSTALL, "bin", "gcc")):
    raise EnvironmentError("GCC_INSTALL is not set correctly or GCC binary is missing.")
if not GCC_BUILD or not os.path.isdir(GCC_BUILD):
    raise EnvironmentError("GCC_BUILD is not set correctly or directory is missing.")
if not EXP_ROOT:
    raise EnvironmentError("EXP_ROOT is not set correctly or directory is missing.")


GCC_PATH = os.path.join(GCC_INSTALL, "bin", "gcc")
GCC_BUILD_DIR = GCC_BUILD

FEATURE = "fuzz4all-seeds"
SUFFIX = "fuzz"
ENABLE_CLEAR = True

# Directories
KITTEN_DIR = os.path.join(EXP_ROOT, "kitten")
SOURCE_DIR = os.path.join(KITTEN_DIR, f"gcc/{FEATURE}/default_mutants_folder")
HANGS_DIR = os.path.join(KITTEN_DIR, f"gcc/{FEATURE}/hangs")
CRASHES_DIR = os.path.join(KITTEN_DIR, f"gcc/{FEATURE}/crashes")
COVERAGE_DIR = os.path.join(KITTEN_DIR, f"gcc/{FEATURE}/coverage")
MAX_HOURS = 24

# Ensure output directories exist
os.makedirs(HANGS_DIR, exist_ok=True)
os.makedirs(CRASHES_DIR, exist_ok=True)
os.makedirs(COVERAGE_DIR, exist_ok=True)

# Get all .c files sorted by modification time
c_files = sorted(Path(SOURCE_DIR).glob(f"*.{SUFFIX}"), key=lambda f: os.path.getmtime(f))

# Initialize counters and time tracking
hangs_count = 0
crashes_count = 0
start_time = datetime.now()
elapsed_compilation_time = timedelta()  # Track only compilation time
hour = 1

if ENABLE_CLEAR:
    subprocess.run(
        ["lcov", "-z", "-d", GCC_BUILD_DIR],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        text=True
    )

def compile_file(file_path):
    """Compile a single .c file and handle hangs or crashes."""
    global hangs_count, crashes_count
    result = subprocess.run(
        ["timeout", "10", GCC_PATH, "-x", "c", "-std=c2x", "-c", str(file_path), "-o", "/dev/null"],
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True
    )
    if result.returncode == 124:  # Timeout (hang)
        shutil.copy(file_path, HANGS_DIR)
        hangs_count += 1
    elif "internal compiler error" in result.stderr.lower():  # Internal compiler error
        shutil.copy(file_path, CRASHES_DIR)
        crashes_count += 1

def collect_coverage(hour):
    """Collect coverage using lcov."""
    coverage_file = os.path.join(COVERAGE_DIR, f"cov_{hour}.info")
    subprocess.run(
        ["lcov", "-c", "-d", GCC_BUILD_DIR, "-o", coverage_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"Coverage collected for hour {hour}: {coverage_file}")

# Start compiling files
with tqdm(total=len(c_files), desc="Compiling files", unit="file") as pbar:
    for file in c_files:
        current_time = datetime.now()
        if elapsed_compilation_time >= timedelta(hours=hour):  # Pause for coverage every hour
            collect_coverage(hour)
            hour += 1
            if hour > MAX_HOURS:  # Stop after 24 hours
                print("Reached maximum compilation time. Stopping.")
                break

        # Compile the file
        file_start_time = datetime.now()
        compile_file(str(file))
        elapsed_compilation_time += datetime.now() - file_start_time

        # Update progress bar
        pbar.set_description(f"Hangs: {hangs_count}, Crashes: {crashes_count}")
        pbar.update(1)

print(f"\nFinished compilation. Total Hangs: {hangs_count}, Total Crashes: {crashes_count}")

