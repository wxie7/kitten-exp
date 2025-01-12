import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Configuration
GCC_PATH = os.path.join(os.getenv("GCC_INSTALL", ""), "bin", "gcc")
SOURCE_DIR = os.path.join(os.getenv("EXP_ROOT", ""), "fuzz4all", "Results", "gcc")
TIMEOUT = 10  # Timeout in seconds
THREAD_COUNT = 24  # Number of threads

if not GCC_PATH or not os.path.exists(GCC_PATH):
    raise EnvironmentError("GCC_INSTALL is not set or the GCC binary does not exist.")

if not SOURCE_DIR or not os.path.isdir(SOURCE_DIR):
    raise EnvironmentError("EXP_ROOT is not set or the source directory does not exist.")

def compile_file(file_path):
    try:
        # Compile command
        command = [
            "timeout", str(TIMEOUT), GCC_PATH,
            "-x", "c", "-std=c2x", "-c", file_path, "-o", "/dev/null"
        ]
        subprocess.run(command, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return (file_path, True)
    except subprocess.CalledProcessError as e:
        return (file_path, False, e)

def compile_fuzz_files_multithreaded():
    # List all .fuzz files in the directory
    fuzz_files = [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.fuzz')]

    if not fuzz_files:
        print("No .fuzz files found in the specified directory.")
        return

    print("Compiling .fuzz files with multithreading...")
    results = []
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {executor.submit(compile_file, file): file for file in fuzz_files}
        for future in tqdm(futures, desc="Processing files", total=len(futures)):
            results.append(future.result())

    # Display summary
    for result in results:
        if result[1]:
            print(f"Compiled successfully: {result[0]}")
        else:
            print(f"Failed to compile: {result[0]} - Error: {result[2]}")

if __name__ == "__main__":
    compile_fuzz_files_multithreaded()

