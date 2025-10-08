import os
import json
from graph import run_migration
from utils.file_ops import prepare_output_dir

SNIPPET_MAX_LEN = 100  # max chars to display per snippet

def main():
    source_repo = r"C:\Users\Mounika.K\Downloads\pra 1 1"

    if not os.path.exists(source_repo):
        print(" Source repo path does not exist:", source_repo)
        return

    # Prepare a single output folder
    dest_repo = prepare_output_dir(base_prefix="cf_repo_")
    print(f" Source Neo repo: {source_repo}")
    print(f" Destination CF repo will be: {dest_repo}\n")

    print(" Running migration workflow...")
    result = run_migration(source_repo, output_path=dest_repo)
    
    # Print migration plan in terminal
    plan = result.get("plan", {}).get("plan", [])
    if plan:
        print("\n Migration Plan:")
        for item in plan:
            file_name = item.get("file")
            action = item.get("action")
            reason = item.get("reason", "")
            snippet = item.get("snippet", "")
            # Shorten snippet for terminal readability
            snippet_short = snippet[:SNIPPET_MAX_LEN].replace("\n", " ") + ("..." if len(snippet) > SNIPPET_MAX_LEN else "")
            target = item.get("target", None)
            print(f" - {file_name} -> action: {action}, target: {target}")
            print(f"   reason: {reason}")
            print(f"   snippet: {snippet_short}\n")
    else:
        print("No files were included in the migration plan.")


    # Print migration completion info
    output_path = result.get("output_path", dest_repo)
    print("\n Migration complete.")
    print(" Output CF-deployable folder:", output_path)

    written_files = result.get("written_files", {})
    if written_files:
        print(" Files written/overwritten:")
        for rel, path in written_files.items():
            print(f" - {rel} -> {path}")
    else:
        print("No files were written.")

if __name__ == "__main__":
    main()
