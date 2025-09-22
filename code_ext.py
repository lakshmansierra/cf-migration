import os

# extensions you want to include (e.g., only Python files)
INCLUDE_EXTENSIONS = {".py"}

# file to write everything into
OUTPUT_FILE = "all_code.txt"

# folders/files you don't want to include
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "code_ext.py"}  
EXCLUDE_FILES = {"__init__.py"}

def collect_code(root="."):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for foldername, subfolders, filenames in os.walk(root):
            # skip excluded dirs
            if any(ex in foldername for ex in EXCLUDE_DIRS):
                continue

            for filename in filenames:
                if filename in EXCLUDE_FILES:
                    continue
                _, ext = os.path.splitext(filename)
                if ext in INCLUDE_EXTENSIONS:
                    filepath = os.path.join(foldername, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            code = f.read()
                        out.write(f"\n\n### File: {filepath}\n\n")
                        out.write(code)
                        out.write("\n" + "="*80 + "\n")  # separator
                    except Exception as e:
                        print(f"⚠️ Could not read {filepath}: {e}")
    print(f"\n✅ All code collected into: {OUTPUT_FILE}")

if __name__ == "__main__":
    collect_code()
