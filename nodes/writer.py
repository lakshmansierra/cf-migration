import os

import json

import base64

from typing import Dict

from utils.file_ops import write_text_file
 
def write_output(dest_repo: str, transformed: Dict[str, str]) -> Dict[str, str]:

    """

    Write transformed files into the destination CF repo.

    Supports:

      - transformer returning plain text (string)

      - transformer returning structured JSON: {"converted_content": "...", "encoding": "utf-8" or "base64"}

    Returns:

      dict mapping rel_target -> full_dest_path

    """

    os.makedirs(dest_repo, exist_ok=True)
 
    written_map: Dict[str, str] = {}

    skipped = []
 
    for target_path, content in transformed.items():

        # validate the relative target path

        if not target_path or target_path.strip() in ["", ".", "/", "\\"]:

            skipped.append(target_path)

            print(f"⚠️ Skipping invalid target path: {target_path!r}")

            continue
 
        dest_path = os.path.join(dest_repo, target_path)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
 
        # If transformer returned JSON string, try to parse it

        file_content = content

        encoding = "utf-8"

        try:

            parsed = json.loads(content)

            if isinstance(parsed, dict):

                file_content = parsed.get("converted_content", "")

                encoding = parsed.get("encoding", "utf-8")

        except (json.JSONDecodeError, TypeError):

            pass  # content is plain text
 
        try:

            if isinstance(encoding, str) and encoding.lower() == "base64":

                with open(dest_path, "wb") as f:

                    f.write(base64.b64decode(file_content))

            else:

                write_text_file(dest_path, file_content)

            written_map[target_path] = dest_path

        except Exception as e:

            skipped.append(target_path)

            print(f"❌ Failed to write {target_path}: {e}")
 
    print(f"\n✅ Wrote {len(written_map)} files to {dest_repo}")

    if skipped:

        print(f"⚠️ Skipped {len(skipped)} files due to invalid paths or errors.")
 
    return written_map

 