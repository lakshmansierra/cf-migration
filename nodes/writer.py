import os
from typing import Dict
from utils.file_ops import write_text_file

def write_output(output_dir: str, repo_root: str, transformed_files: Dict[str, str]) -> Dict[str, str]:
    """
    Writes all transformed files to the output folder, preserving relative paths.

    Args:
        output_dir: Base CF output folder.
        repo_root: Original repo path (for reference, not used directly here).
        transformed_files: Dict of relative file paths -> content.

    Returns:
        Dict of written files with their absolute paths.
    """
    written_files = {}

    for rel_path, content in transformed_files.items():
        # Determine full path in the output folder
        dest_path = os.path.join(output_dir, rel_path)

        # Ensure all parent directories exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Write content
        write_text_file(dest_path, content)

        written_files[rel_path] = dest_path

    return written_files
