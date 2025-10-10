import os
from typing import Dict, Tuple
from utils.file_ops import write_text_file

def write_output(transformed_files: Dict[str, str], output_dir: str) -> Tuple[str, Dict[str, str]]:
    os.makedirs(output_dir, exist_ok=True)
    written: Dict[str, str] = {}

    for rel_target, content in transformed_files.items():
        if rel_target.endswith("/") or rel_target.endswith("\\"):
            continue
        dest_path = os.path.join(output_dir, rel_target)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        write_text_file(dest_path, content)
        written[rel_target] = dest_path

    return output_dir, written