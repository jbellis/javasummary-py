import sys
import os
import javalang
from pathlib import Path

# The java_summary.py script should be in the same directory
from java_summary import summarize_java_file

def process_directory(path, base_path):
    summaries = []

    # Iterate through all .java files in the directory
    for full_path in path.glob("*.java"):
        filename = full_path.name
        if filename in {"package-info.java", "module-info.java"}:
            continue
        try:
            summary = summarize_java_file(str(full_path))
        except javalang.parser.JavaSyntaxError as e:
            raise Exception(f"Error parsing {full_path}: {e}")
        if summary:
            summaries.append(summary)

    # If there are any summaries, print the package name
    if summaries:
        package_path = path.relative_to(base_path).as_posix().replace("/", ".")
        print(f"# package {package_path}")
        print("\n".join(summaries))

    # Recursively process subdirectories
    for subdir in path.iterdir():
        if subdir.is_dir():
            process_directory(subdir, base_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python java_tree_summary.py <path_to_java_source_tree>")
        sys.exit(1)

    java_source_tree = Path(sys.argv[1]).resolve()
    process_directory(java_source_tree, java_source_tree)
