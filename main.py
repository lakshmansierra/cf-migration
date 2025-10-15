import os
from graph import run_migration
from utils.file_ops import prepare_output_dir

def main():
    source_repo = r"F:\downloads\pra 1 1"
    
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
    written = result.get("written_files", {})
    # If writer returned a list (legacy behavior), convert to rel->full mapping
    if isinstance(written, list):
        written = {os.path.relpath(p, output_path): p for p in written}
    for rel, path in written.items():
        print(" -", rel, "->", path)

if __name__ == "__main__":
    main()