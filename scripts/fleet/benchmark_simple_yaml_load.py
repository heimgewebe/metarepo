import time
import os
import sys
import tracemalloc

# Add script directory to path to import the function
sys.path.append('scripts/fleet')
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
            # Avoid the bug by using non-boolean values for now if I haven't fixed it yet
            f.write("      status: related\n")
            f.write("      fleet: yes\n")

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
    mock_file = "fleet/mock_repos.yml"
    print(f"Creating large mock file: {mock_file}")
    create_large_mock_yaml(mock_file, num_repos=500000) # Large enough to see difference

    print("Starting benchmark...")
    avg_time, peak_mem = benchmark(mock_file)
    print(f"Average execution time: {avg_time:.4f} seconds")
    print(f"Peak memory usage: {peak_mem:.4f} MB")

    # Clean up
    if os.path.exists(mock_file):
        os.remove(mock_file)
