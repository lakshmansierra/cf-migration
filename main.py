import os
from graph import run_migration
from utils.file_ops import prepare_output_dir
import json

def main():
    source_repo = r"C:\Users\stalin\Documents\cf\pra 1 1 (1)"

    if not os.path.exists(source_repo):
        print(f" Source repo path does not exist: {source_repo}")
        return

    `dest_repo = prepare_output_dir(base_prefix="cf_repo_")
    print(f" Source Neo repo: {source_repo}")
    print(f" Destination CF repo will be: {dest_repo}")

    result = run_migration(source_repo)

    if not result:
        print(" Migration returned no results. Please check logs.")
        return

    print("\n Migration Plan:")
    if "plan" in result:
        print(json.dumps(result["plan"], indent=2))

    print("\n Migration complete.")
    output_path = result.get("output_path", dest_repo)
    print(f"Output CF-deployable folder: {output_path}")

    written_files = result.get("written_files", {})
    if written_files:
        print("\n Files written/overwritten:")
        for rel, path in written_files.items():
            print(f" - {rel} -> {path}")
    else:
        print("No files were written.")

if __name__ == "__main__":
    main()