import os
import json
from utils.file_ops import prepare_output_dir
from nodes.planner import plan_migration
from nodes.transformer import transform_files, save_transformed_files
from nodes.writer import write_output

def main():
    source_repo = r"F:\downloads\pra 1 1"
    
    if not os.path.exists(source_repo):
        print("Source repo path does not exist:", source_repo)
        return

    # 1️⃣ Prepare CF output folder
    dest_repo = prepare_output_dir(base_prefix="cf_repo_")
    print("Source Neo repo:", source_repo)
    print("Destination CF repo will be:", dest_repo)

    # 2️⃣ Generate migration plan
    plan, snippets = plan_migration(source_repo)
    print("\nMigration Plan:")
    print(json.dumps(plan, indent=2))

    # 3️⃣ Decide CF app name (can be parsed from neo-app.json)
    app_name = "my_app"

    # 4️⃣ Transform files (content & paths)
    transformed = transform_files(source_repo, plan, app_name)

    # 5️⃣ Write transformed files to CF structure
    written_files = write_output(dest_repo, source_repo, transformed)

    print("\nMigration complete.")
    print("Output CF-deployable folder:", dest_repo)
    print("Files written/overwritten:")
    for rel, path in written_files.items():
        print(" -", rel, "->", path)

if __name__ == "__main__":
    main()
