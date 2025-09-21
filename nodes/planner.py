import os
import json
import re
from typing import Dict, Any
from utils.aicore_client import AICoreClient

SYSTEM_PROMPT = """
You are an expert assistant that detects which files in an SAP Neo application repository must be migrated to run on SAP Cloud Foundry.
Output a JSON object with a single key "plan" whose value is a list of objects with:
- file: relative path (string)
- reason: short reason (string)
- action: one of ["convert_manifest", "remove_neo_route", "convert_mta", "convert_xsapp", "copy_as_is", "manual_review"]
- target: suggested target filename if action creates new file (or null)
Return only valid JSON.
"""

def plan_migration(repo_root: str, model_name: str = "gpt-4") -> Dict[str, Any]:
    """
    Inspect repo files and ask AI Core which ones to migrate.
    """
    client = AICoreClient()

    # Gather repo files
    filenames = []
    snippets = {}
    for root, _, files in os.walk(repo_root):
        for fn in files:
            filenames.append(os.path.join(root, fn))

    rel_files = [os.path.relpath(f, repo_root) for f in filenames][:400]

    interesting = ["neo-app.json", "mta.yaml", "xs-app.json", "xs-security.json", "manifest.yml"]
    for f in filenames:
        if os.path.basename(f) in interesting:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    snippets[os.path.relpath(f, repo_root)] = fh.read()[:4000]
            except Exception:
                snippets[os.path.relpath(f, repo_root)] = "<unreadable>"

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Repo context (JSON): {json.dumps({'filenames': rel_files, 'snippets': snippets}, indent=2)}\n"
                           f"Produce a migration plan as JSON with key 'plan'."
            },
        ]
    }

    resp = client.invoke_model(model_name, payload)
    text = resp.get("result", {}).get("choices", [{}])[0].get("message", {}).get("content", "").strip()

    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            return json.loads(m.group(0))
        return {"plan": []}
