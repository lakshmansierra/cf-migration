# nodes/transformer.py
import os
import json
from typing import Dict, Any
from utils.file_ops import read_text_file

from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage

llm = ChatOllama(model="mistral:latest")

SYSTEM_PROMPT = """
You are a migration assistant that converts SAP Neo config files and application files to Cloud Foundry equivalents.
You will receive a JSON object containing:
- file_name: relative path (string)
- action: one of [convert_manifest, remove_neo_route, convert_mta, convert_xsapp, copy_as_is, manual_review]
- file_content: the source file content (string)

For actions that produce a new file (e.g. convert_manifest), return the converted file content only.
For copy_as_is, return the original content unchanged.
If you cannot convert, return a JSON object like {"error":"reason"}.
 
Return only the transformed file content or the small error JSON.
"""

def transform_files(repo_root: str, plan: Dict[str, Any]) -> Dict[str, str]:
    results: Dict[str, str] = {}
    items = plan.get("plan", [])

    for item in items:
        rel = item.get("file")
        action = item.get("action")
        target = item.get("target") or rel
        src_path = os.path.join(repo_root, rel)
        if not os.path.exists(src_path):
            results[target] = f"# MISSING SOURCE: {rel}\n"
            continue
        content = read_text_file(src_path)
        payload = {
            "file_name": rel,
            "action": action,
            "file_content": content,
            "instructions": SYSTEM_PROMPT
        }
        prompt = json.dumps(payload, indent=2)

        # Use ChatOllama directly
        resp = llm.invoke([HumanMessage(content=prompt)])

        results[target] = resp
    return results
