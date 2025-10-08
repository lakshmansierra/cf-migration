import os
import json
import shutil
import tempfile

def prepare_output_dir(base_prefix: str = "cf_migrated_") -> str:
    path = tempfile.mkdtemp(prefix=base_prefix)
    print(f"[INFO] Created output directory: {path}")
    return path

def copy_repo_to_output(src_repo_path: str, dest_output_path: str) -> None:
    if not os.path.exists(src_repo_path):
        raise FileNotFoundError(f"Source repo path not found: {src_repo_path}")

    for root, dirs, files in os.walk(src_repo_path):
        rel = os.path.relpath(root, src_repo_path)
        dest_root = os.path.join(dest_output_path, rel) if rel != "." else dest_output_path
        os.makedirs(dest_root, exist_ok=True)
        for d in dirs:
            os.makedirs(os.path.join(dest_root, d), exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), os.path.join(dest_root, f))

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_text_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def save_dict_to_file(data: dict, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
