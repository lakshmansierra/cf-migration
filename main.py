import os
from graph import run_migration

def main():
    repo_path = r"C:\Users\LakshmanNavaneethakr\AppData\Local\Temp\neo_cf_repo_g3dvzn2i"
    os.environ["OPENAI_API_KEY"] = "sk-your-key-here"

    if not os.path.exists(repo_path):
        print("Repo path does not exist:", repo_path)
        return

    print("Starting migration for:", repo_path)
    result = run_migration(repo_path)
    print("Migration complete.")
    print("Output folder:", result["output_path"])
    print("Files written/overwritten:")
    for rel, path in result["written_files"].items():
        print(" -", rel, "->", path)

if __name__ == "__main__":
    main()
