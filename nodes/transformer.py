# neo_cf_migrator/nodes/transformer.py
import os
from typing import Dict

def transform_files(state: Dict) -> Dict:
    repo_path = state["repo_path"]
    plan = state["plan"]

    transformed_files = {}

    for file_name in plan["files_to_check"]:
        file_path = os.path.join(repo_path, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            # Dummy transformation (later we’ll add real rules)
            new_content = content.replace("neo", "cf_migrated")

            transformed_files[file_name] = new_content

    state["transformed_files"] = transformed_files
    return state
