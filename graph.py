from typing import Dict, Any
from utils.file_ops import prepare_output_dir
from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output

def run_migration(repo_path: str) -> Dict[str, Any]:
    """
    End-to-end run:
      1. Plan (LLM)
      2. Transform (LLM)
      3. Write outputs (copy + overwrite)
    Returns: { output_path, written_files, plan }
    """
    # create output dir
    output_path = prepare_output_dir()

    # 1. Plan
    plan = plan_migration(repo_path)

    # 2. Transform
    transformed_files = transform_files(repo_path, plan)

    # 3. Write files (copy repo then overwrite converted files)
    written = write_output(output_path, repo_path, transformed_files)

    return {
        "output_path": output_path,
        "written_files": written,
        "plan": plan
    }
