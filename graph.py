from typing import Dict, Any
from utils.file_ops import read_text_file
from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output
import os

def run_migration(source_repo: str, output_dir: str) -> Dict[str, Any]:
    print(" Planning migration...")
    plan, snippets = plan_migration(source_repo)
    if not plan:
        print(" No migration plan generated.")
        return None

    print(" Transforming files based on migration plan...")
    transformed_files = transform_files(source_repo, plan, snippets, output_dir)
    if not transformed_files:
        print(" No files were transformed.")
        return None

    print(" Writing transformed files to destination folder...")
    written_path, written_files = write_output(transformed_files, output_dir)

    print(" Migration workflow complete.")
    return {
        "plan": plan,
        "output_path": written_path,
        "written_files": written_files,
    }