# utils/file_ops.py
import os
import shutil
import tempfile
from typing import List

def prepare_output_dir(base_prefix: str = "cf_migrated_") -> str:
    """Create a temp output directory and return its path."""
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

def write_text_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


