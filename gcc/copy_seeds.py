import os
import subprocess
from tqdm import tqdm
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Constants
GCC_INSTALL = os.getenv("GCC_INSTALL")
GCC_SRC = os.getenv("GCC_SRC")
TESTSUITE_DIRS = ["c-c++-common", "gcc.c-torture", "gcc.dg"]
if not GCC_INSTALL:
    print("GCC_INSTALL environment variable not set.")
    exit(1)
if not GCC_SRC:
    print("GCC_SRC environment variable not set.")
    exit(1)

GCC_SEEDS_DIR = os.getenv("GCC_SEEDS")
if not GCC_SEEDS_DIR:
    print("GCC_SEEDS_DIR environment variable not set.")
    exit(1)
os.makedirs(GCC_SEEDS_DIR, exist_ok=True)

GCC_COMMAND = os.path.join(GCC_INSTALL, "bin", "gcc")
COMPILE_ARGS = [
    "-x", "c",
    "-std=c2x",
    "-c"
]
TIMEOUT = 30

# Global counters
ice_count = 0
timeout_count = 0
lock = None  # For thread-safe counter updates

def compile_file(c_file):
    global ice_count, timeout_count
    cmd = [
        "timeout", str(TIMEOUT), GCC_COMMAND,
        *COMPILE_ARGS, c_file,
        "-o", "/dev/null"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode == 124:  # Timeout
        with lock:
            timeout_count += 1
        return ("timeout", c_file)
    elif "internal compiler error" in result.stderr:
        with lock:
            ice_count += 1
        return ("ice", c_file)
    else:
        shutil.copy(c_file, GCC_SEEDS_DIR)
        return ("success", c_file)

def main():
    global lock
    lock = Lock()

    c_files = []
    for testsuite in TESTSUITE_DIRS:
        for dirpath, _, filenames in os.walk(os.path.join(GCC_SRC, "gcc", "testsuite", testsuite)):
            for file in filenames:
                if file.endswith(".c"):
                    c_files.append(os.path.join(dirpath, file))

    progress_bar = tqdm(total=len(c_files), desc="Compiling .c files", unit="file")

    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(compile_file, c_file): c_file for c_file in c_files}

        for future in as_completed(future_to_file):
            result, c_file = future.result()

            if result == "timeout":
                progress_bar.set_postfix(ICE=ice_count, Timeout=timeout_count)
                print(f"Timeout: {c_file}")
            elif result == "ice":
                progress_bar.set_postfix(ICE=ice_count, Timeout=timeout_count)
                print(f"ICE: {c_file}")

            progress_bar.update(1)

    progress_bar.close()
    print(f"Compilation completed. ICE: {ice_count}, Timeouts: {timeout_count}")

if __name__ == "__main__":
    main()

