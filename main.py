import os
import json
from utils.file_ops import prepare_output_dir
from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output


def main():
    # 1️⃣ Define source repo path
    source_repo = r"F:\downloads\pra 1 1"

    if not os.path.exists(source_repo):
        print("❌ Source repo path does not exist:", source_repo)
        return

    # 2️⃣ Prepare CF output folder
    dest_repo = prepare_output_dir(base_prefix="cf_repo_")
    print(f"\n📂 Source Neo repo: {source_repo}")
    print(f"📁 Destination CF repo will be: {dest_repo}")

    # 3️⃣ Generate migration plan
    plan, snippets = plan_migration(source_repo)
    print("\n🧭 Migration Plan generated successfully.")
    print(json.dumps(plan, indent=2))

    # 4️⃣ Decide CF app name (can later parse from neo-app.json)
    app_name = "my_app"

    # 5️⃣ Transform files according to the plan
    print("\n⚙️ Transforming files...")
    transformed = transform_files(source_repo, plan, app_name)

    # 6️⃣ Write transformed output to CF folder
    print("\n💾 Writing transformed files to output...")
    written_files = write_output(dest_repo, transformed)

    # 7️⃣ Summary
    print("\n✅ Migration complete!")
    print(f"📦 Cloud Foundry-deployable folder: {dest_repo}")
    print("🗂️ Files written:")
    for path in written_files:
        print(f" - {path}")


if __name__ == "__main__":
    main()
