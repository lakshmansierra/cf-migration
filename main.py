import os
from graph import run_migration
from utils.file_ops import prepare_output_dir

def main():
    source_repo = r"C:\Users\Mounika.K\Downloads\pra 1 1"
    
    if not os.path.exists(source_repo):
        print("Source repo path does not exist:", source_repo)
        return

    dest_repo = prepare_output_dir(base_prefix="cf_repo_")
    print("Source Neo repo:", source_repo)
    print("Destination CF repo will be:", dest_repo)

    result = run_migration(source_repo)

    output_path = result.get("output_path", dest_repo)
    print("\nMigration complete.")
    print("Output CF-deployable folder:", output_path)
    print("Files written/overwritten:")
    for rel, path in result.get("written_files", {}).items():
        print(" -", rel, "->", path)

if __name__ == "__main__":
    main()
