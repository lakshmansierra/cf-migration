import os
from typing import Dict
from utils.file_ops import copy_repo_to_output, write_text_file

def write_output(output_root: str, repo_root: str, transformed_files: Dict[str, str]) -> Dict[str, str]:
    """
    Write only the transformed CF files to the output folder
    (without copying the original Neo repo).
    """
    os.makedirs(output_root, exist_ok=True)

    written = {}
    for rel_target, content in transformed_files.items():
        dest_path = os.path.join(output_root, rel_target)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
        written[rel_target] = dest_path

    return written

