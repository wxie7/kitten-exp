import os
import sys
import subprocess
import csv
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def merge_coverage_files(left, right):
    """Merge coverage files such that cov_i is merged into cov_(i+1)."""
    for i in range(left, right):
        current_file = f"cov_{i}.info"
        next_file = f"cov_{i + 1}.info"
        if os.path.exists(current_file) and os.path.exists(next_file):
            merge_cmd = ["lcov", "-a", current_file, "-a", next_file, "-o", next_file]
            subprocess.run(merge_cmd, check=True)
            print(f"Merged {current_file} into {next_file}.")
        else:
            print(f"Skipping merge: {current_file} or {next_file} not found.")

def capture_coverage(file, hour):
    """Capture the number of covered lines from a specific coverage file."""
    summary_cmd = ["lcov", "--summary", file]
    try:
        result = subprocess.run(summary_cmd, check=True, stdout=subprocess.PIPE, text=True)
        output = result.stdout
        # Extract covered lines (e.g., "460649")
        match = re.search(r"lines\.*:\s*[\d.]+%\s+\((\d+) of", output)
        if match:
            return [hour, int(match.group(1))]
        else:
            print(f"No coverage data found in {file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating summary for {file}: {e}")
    return [hour, 0]

def multithreaded_capture_coverage(left, right, output_csv="coverage_summary.csv"):
    """Use multithreading to capture coverage for each hour."""
    rows = [["hour", "lines"]]
    with ThreadPoolExecutor() as executor:
        future_to_hour = {
            executor.submit(capture_coverage, f"cov_{hour}.info", hour): hour
            for hour in range(left, right + 1)
        }
        for future in tqdm(as_completed(future_to_hour), total=len(future_to_hour), desc="Capturing coverage"):
            hour = future_to_hour[future]
            try:
                rows.append(future.result())
            except Exception as e:
                print(f"Error processing hour {hour}: {e}")
    rows = [rows[0]] + sorted(rows[1:], key=lambda x: x[0])
    # Write to CSV
    with open(output_csv, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)
    print(f"Coverage summary saved to {output_csv}.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 merge_coverage_to_csv.py <left> <right> [output_csv]")
        sys.exit(1)
    
    left = int(sys.argv[1])
    right = int(sys.argv[2])
    output_csv = sys.argv[3] if len(sys.argv) > 3 else "lines.csv"
    
    # Step 1: Merge files progressively
    merge_coverage_files(left, right)
    # Step 2: Capture coverage in parallel
    multithreaded_capture_coverage(left, right, output_csv)

if __name__ == "__main__":
    main()
