# main.py
import os
from graph import run_migration
from utils.file_ops import prepare_output_dir

def main():
    # Hardcoded source repo (Neo environment)
    source_repo = r"C:\Users\LakshmanNavaneethakr\Downloads\Others\pra 1 1"
    

    if not os.path.exists(source_repo):
        print("Source repo path does not exist:", source_repo)
        return

    # Hardcoded destination repo path (new CF-deployable repo)
    # We create a new folder inside temp with prefix
    dest_repo = prepare_output_dir(base_prefix="cf_repo_")
    print("Source Neo repo:", source_repo)
    print("Destination CF repo will be:", dest_repo)

    # Run migration
    result = run_migration(source_repo)

    # The output path from the workflow will be a temp folder created by the writer
    output_path = result.get("output_path", dest_repo)
    print("\nMigration complete.")
    print("Output CF-deployable folder:", output_path)
    print("Files written/overwritten:")
    for rel, path in result.get("written_files", {}).items():
        print(" -", rel, "->", path)

if __name__ == "__main__":
    main()
