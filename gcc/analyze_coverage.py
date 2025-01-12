import csv
import sys
import os

def is_front_end(path):
    return 'c-' in path or \
           'parse' in path or \
           'generic' in path or \
           'type' in path or \
           'gimplify' in path

def is_middle_or_back_end(path):
    return 'config' in path or \
           'gimple' in path or \
           'ssa' in path or \
           'ipa' in path or \
           'rtl' in path or \
           'tree' in path or \
           'ira' in path or \
           'insn' in path or \
           'sched' in path or \
           'reg' in path or \
           'cfg' in path or \
           'cgraph' in path or \
           'dwarf' in path

def parse_lcov_info(info_file):
    """
    Parse lcov info file and return coverage data.
    """
    coverage_data = {}
    current_file = None
    covered_lines = 0
    uncovered_lines = 0

    with open(info_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("SF:"):
                if current_file is not None:
                    coverage_data[current_file] = (covered_lines, uncovered_lines)
                current_file = line[3:]
                covered_lines = 0
                uncovered_lines = 0
            if line.startswith("DA:"):
                _, line_info = line.split(":")
                line_num, exec_count = map(int, line_info.split(","))
                if exec_count > 0:
                    covered_lines += 1
                else:
                    uncovered_lines += 1
        if current_file is not None:
            coverage_data[current_file] = (covered_lines, uncovered_lines)
    return coverage_data

def collect_coverage_info(coverage_data):
    front_end_lines = 0
    middle_or_back_end_lines = 0
    other_lines = 0

    for filename, (covered_lines, _) in coverage_data.items():
        filename = os.path.basename(filename)
        if is_front_end(filename):
            front_end_lines += covered_lines
        elif is_middle_or_back_end(filename):
            middle_or_back_end_lines += covered_lines
        else:
            other_lines += covered_lines

    print(f"Front-end coverage lines: {front_end_lines}")
    print(f"Middle/Back-end coverage lines: {middle_or_back_end_lines}")
    print(f"Other coverage lines: {other_lines}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_coverage.py <info_file>")
        sys.exit(1)

    info_file = sys.argv[1]

    # Parse lcov info file
    coverage_data = parse_lcov_info(info_file)

    # Collect and print coverage info
    collect_coverage_info(coverage_data)

if __name__ == "__main__":
    main()
