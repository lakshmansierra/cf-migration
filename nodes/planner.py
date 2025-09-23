import os
import json
from typing import Dict, Any, List
from utils.file_ops import read_text_file, save_dict_to_file

from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage

llm = ChatOllama(model="mistral:latest")

SYSTEM_INSTRUCTIONS = """
You are an expert assistant that inspects a repository layout for an SAP Neo application and
produces a migration plan to run on Cloud Foundry.

Input you'll receive (as JSON):
- filenames: list of relative file paths (strings)
- snippets: mapping of relpath -> file snippet (small text)
Your output MUST be valid JSON of the form:
{
  "plan": [
    {
      "file": "<relative/path/to/file>",
      "reason": "<short reason>",
      "action": "<one of convert_manifest, remove_neo_route, convert_mta, convert_xsapp, copy_as_is, manual_review>",
      "target": "<suggested target filename or null>"
    },
    ...
  ]
}
Return only this JSON. If nothing to do, return {"plan": []}.
"""

def _gather(repo_root: str, max_files: int = 400, max_snippets: int = 50) -> Dict[str, Any]:
    filenames: List[str] = []
    snippets: Dict[str, str] = {}
    for root, _, files in os.walk(repo_root):
        for f in files:
            filenames.append(os.path.relpath(os.path.join(root, f), repo_root))
    filenames = sorted(filenames)[:max_files]

    interesting = {
    "neo-app.json",
    "mta.yaml",
    "mta.yml",
    "xs-security.json",
    "manifest.yml",
    "package.json"  # only if it's a Node.js project
}
    count = 0
    for rel in filenames:
        base = os.path.basename(rel)
        if base in interesting and count < max_snippets:
            try:
                # only reads interesting files, not all repo files, coz it is not language conversion
                snippets[rel] = read_text_file(os.path.join(repo_root, rel))
                # snippets[rel] = read_text_file(os.path.join(repo_root, rel))[:4000]
            except:
                snippets[rel] = "<unreadable>"
            count += 1
    return {"filenames": filenames, "snippets": snippets}

def plan_migration(repo_root: str) -> Dict[str, Any]:
    payload = _gather(repo_root)

    save_dict_to_file(payload, os.path.join(repo_root, "_gather_return.txt"))

    prompt_obj = {
        "instructions": SYSTEM_INSTRUCTIONS,
        "filenames": payload["filenames"],
        "snippets": payload["snippets"]
    }
    prompt = json.dumps(prompt_obj, indent=2)

    resp = llm.invoke([HumanMessage(content=prompt)])

    try:
        parsed = json.loads(resp)
        if "plan" in parsed and isinstance(parsed["plan"], list):
            save_dict_to_file(parsed, "plan_migration_return.txt")  # save only valid plan
            return parsed
    except Exception:
        pass

    return {"plan": []}
