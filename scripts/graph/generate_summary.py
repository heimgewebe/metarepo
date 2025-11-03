import json
from pathlib import Path

data = json.loads(Path('reports/graphs/deps_graph.json').read_text())
nodes = len(data.get('nodes', []))
edges = len(data.get('links', []))
print(f"Nodes: {nodes}")
print(f"Edges: {edges}")
