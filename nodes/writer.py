# nodes/writer.py
import os
from typing import Dict
from utils.file_ops import copy_repo_to_output, write_text_file

def write_output(output_root: str, repo_root: str, transformed_files: Dict[str, str]) -> Dict[str, str]:
    """
    - Copy full repo to output_root
    - Overwrite transformed files into the output_root paths
    Returns mapping of written files.
    """
    # Step A: copy repo to output root
    os.makedirs(output_root, exist_ok=True)
    copy_repo_to_output(repo_root, output_root)

    written = {}
    for rel_target, content in transformed_files.items():
        dest_path = os.path.join(output_root, rel_target)
        write_text_file(dest_path, content)
        written[rel_target] = dest_path

    return written
