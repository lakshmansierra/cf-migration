# neo_cf_migrator/main.py
from graph import build_graph

def run_migration(repo_path: str):
    graph = build_graph()
    result = graph.invoke({"repo_path": repo_path})
    return result

if __name__ == "__main__":
    repo_path = "/tmp/neo_cf_repo_xyz"  # Example cloned repo path
    result = run_migration(repo_path)
    print("Migration complete. New folder:", result["output_path"])
