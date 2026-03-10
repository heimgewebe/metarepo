import time
import os
import sys
import tracemalloc
from pathlib import Path

# Add script directory to path to import the function robustly
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from generate_fleet_docs import simple_yaml_load

def create_large_mock_yaml(filepath, num_repos=100000):
    with open(filepath, 'w') as f:
        f.write("repos:\n")
        for i in range(num_repos):
            f.write(f"  - name: repo-{i}\n")
        f.write("static:\n")
        f.write("  include:\n")
        for i in range(100):
            f.write(f"    - name: static-{i}\n")
            f.write("      status: related\n")
            # Use boolean values to exercise the parsing fix
            f.write(f"      fleet: {'true' if i % 2 == 0 else 'false'}\n")

def benchmark(filepath, iterations=1):
    tracemalloc.start()
    start_time = time.perf_counter()

    for _ in range(iterations):
        simple_yaml_load(filepath)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return (end_time - start_time) / iterations, peak / 1024 / 1024 # Time in s, Peak memory in MB

if __name__ == "__main__":
    # Use path relative to repo root if possible, or same dir as script
    repo_root = Path(__file__).resolve().parent.parent.parent
    mock_file = repo_root / "fleet" / "mock_repos.yml"

    if not mock_file.parent.exists():
        mock_file = Path("mock_repos.yml")

    print(f"Creating large mock file: {mock_file}")
    create_large_mock_yaml(mock_file, num_repos=500000) # Large enough to see difference

    print("Starting benchmark...")
    avg_time, peak_mem = benchmark(str(mock_file))
    print(f"Average execution time: {avg_time:.4f} seconds")
    print(f"Peak memory usage: {peak_mem:.4f} MB")

    # Quick functional check
    data = simple_yaml_load(str(mock_file))
    if data["static"]["include"]:
        first_fleet = data["static"]["include"][0].get("fleet")
        print(f"Functional check: first static repo fleet status is {first_fleet} (type: {type(first_fleet)})")

    # Clean up
    if os.path.exists(mock_file):
        os.remove(mock_file)
