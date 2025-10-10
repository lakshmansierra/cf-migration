import os
import json
import base64

def write_output(dest_repo, transformed):
    """
    Write transformed files into the destination CF repo.
    Handles both plain text and structured JSON-based outputs.
    """

    written_files = []
    skipped_files = []

    for target_path, content in transformed.items():
        # 🧩 Validate path
        if not target_path or target_path.strip() in [".", "/", "\\"]:
            skipped_files.append(target_path)
            print(f"⚠️ Skipping invalid target path: {target_path!r}")
            continue

        # Construct destination file path
        dest_path = os.path.join(dest_repo, target_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # 🔍 Handle if 'content' is JSON (structured transformer output)
        try:
            obj = json.loads(content)
            file_content = obj.get("converted_content", "")
            encoding = obj.get("encoding", "utf-8")
        except (json.JSONDecodeError, TypeError):
            file_content = content
            encoding = "utf-8"

        # 🧾 Write file based on encoding
        try:
            if encoding == "base64":
                with open(dest_path, "wb") as f:
                    f.write(base64.b64decode(file_content))
            else:
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
            written_files.append(dest_path)
        except Exception as e:
            skipped_files.append(target_path)
            print(f"❌ Failed to write {target_path}: {e}")

    print(f"\n✅ Wrote {len(written_files)} files to {dest_repo}")
    if skipped_files:
        print(f"⚠️ Skipped {len(skipped_files)} files due to invalid paths or errors.")
    return written_files
