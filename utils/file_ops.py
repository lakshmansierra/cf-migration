import os
import json
import shutil
import tempfile
from typing import Any, Dict
 
# ------------------------
# Output Folder Utilities
# ------------------------
 
def prepare_output_dir(base_prefix: str = "cf_migrated_") -> str:
    """
    Create a temporary output directory for CF migration.
    Returns the absolute path.
    """
    return tempfile.mkdtemp(prefix=base_prefix)
 
 
def copy_repo_to_output(src_repo_path: str, dest_output_path: str) -> None:
    """
    Copy entire source repository into output folder while preserving folder structure.
    """
    if not os.path.exists(src_repo_path):
        raise FileNotFoundError(f"Source repo path not found: {src_repo_path}")
 
    for root, dirs, files in os.walk(src_repo_path):
        rel_root = os.path.relpath(root, src_repo_path)
        dest_root = os.path.join(dest_output_path, rel_root) if rel_root != "." else dest_output_path
        os.makedirs(dest_root, exist_ok=True)
 
        # Ensure all subdirectories exist
        for d in dirs:
            os.makedirs(os.path.join(dest_root, d), exist_ok=True)
 
        # Copy all files
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(dest_root, f)
            shutil.copy2(src_file, dst_file)
 
# ------------------------
# File Read/Write Utilities
# ------------------------
 
def read_text_file(path: str) -> str:
    """
    Read a text file, ignoring encoding errors.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
 
 
def write_text_file(path: str, content: str) -> None:
    """
    Write a text file, creating parent directories if necessary.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
 
 
def save_dict_to_file(data: Dict[str, Any], file_path: str) -> None:
    """
    Save a dictionary to a JSON file, creating parent directories if needed.
    """
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
 
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)