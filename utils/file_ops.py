import os
import json
import shutil
import tempfile
from typing import Any, Dict


def prepare_output_dir(base_prefix: str = "cf_migrated_") -> str:
    return tempfile.mkdtemp(prefix=base_prefix)

def copy_repo_to_output(src_repo_path: str, dest_output_path: str) -> None:
    """
    Copy entire repository into output folder (preserve structure).
    """
    if not os.path.exists(src_repo_path):
        raise FileNotFoundError(f"Source repo path not found: {src_repo_path}")

    # Copy content recursively
    for root, dirs, files in os.walk(src_repo_path):
        rel = os.path.relpath(root, src_repo_path)
        dest_root = os.path.join(dest_output_path, rel) if rel != "." else dest_output_path
        os.makedirs(dest_root, exist_ok=True)
        for d in dirs:
            os.makedirs(os.path.join(dest_root, d), exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(dest_root, f)
            shutil.copy2(src_file, dst_file)

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

import os

def write_text_file(path, content):
    """Write text to a file, skipping directories by mistake."""
    # If the path is a directory, skip writing
    if os.path.isdir(path):
        print(f" Skipping write — path is a directory: {path}")
        return

    # Make sure parent folders exist
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write the file
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def save_dict_to_file(data: Dict[str, Any], file_path: str) -> None:
    """
    Save a dictionary to JSON file. Create parent dir only if needed.
    """
    # Ensure directory exists only if file_path contains a directory part
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    # Write JSON atomically (optional: simple implementation)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)