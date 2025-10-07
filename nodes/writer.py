import os
from typing import Dict
from utils.file_ops import copy_repo_to_output, write_text_file

def write_output(output_root: str, repo_root: str, transformed_files: Dict[str, str]) -> Dict[str, str]:
    """
    Writes a CF-deployable repo:
    - Copies entire source repo to output_root
    - Overwrites transformed files into the output paths
    - Returns mapping of written files
    """
    # Ensure output folder exists
    os.makedirs(output_root, exist_ok=True)

    # Copy full repo structure first
    copy_repo_to_output(repo_root, output_root)

    # Overwrite transformed files
    written = {}
    for rel_target, content in transformed_files.items():
        dest_path = os.path.join(output_root, rel_target)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        write_text_file(dest_path, content)
        written[rel_target] = dest_path

    return written
