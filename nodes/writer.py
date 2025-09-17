# neo_cf_migrator/nodes/writer.py
import os
import tempfile
from typing import Dict

def write_output(state: Dict) -> Dict:
    transformed_files = state["transformed_files"]

    output_dir = tempfile.mkdtemp(prefix="cf_migrated_")

    for file_name, content in transformed_files.items():
        new_path = os.path.join(output_dir, file_name)
        with open(new_path, "w") as f:
            f.write(content)

    state["output_path"] = output_dir
    return state
