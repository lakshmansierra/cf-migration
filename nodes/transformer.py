import os
from typing import Dict, Any
from utils.aicore_client import AICoreClient

SYSTEM_PROMPT = """
You are a migration assistant that converts SAP Neo config files to Cloud Foundry equivalents.
For each input file content and action, output the converted file content only (no extra commentary).
If you cannot convert fully, return a JSON object {"error":"explain reason"}.
"""

def transform_files(repo_root: str, plan: Dict[str, Any], model_name: str = "gpt-4") -> Dict[str, str]:
    """
    For each plan item, read the file and call AI Core to produce converted content.
    """
    client = AICoreClient()
    results: Dict[str, str] = {}

    for item in plan.get("plan", []):
        file_rel = item.get("file")
        action = item.get("action")
        target = item.get("target") or file_rel
        src_abspath = os.path.join(repo_root, file_rel)

        if not os.path.exists(src_abspath):
            continue

        try:
            with open(src_abspath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = ""

        prompt = _make_prompt(action, content, file_rel)

        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        }

        resp = client.invoke_model(model_name, payload)
        txt = resp.get("result", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        results[target] = txt

    return results

def _make_prompt(action: str, content: str, filename: str) -> str:
    if action == "convert_manifest":
        return f"Convert this Neo config ({filename}) into a Cloud Foundry manifest.yml:\n{content}"
    elif action == "convert_mta":
        return f"Convert this mta.yaml into a Cloud Foundry manifest.yml:\n{content}"
    elif action == "convert_xsapp":
        return f"Convert this xs-app.json into Cloud Foundry routes:\n{content}"
    elif action == "copy_as_is":
        return content
    elif action == "manual_review":
        return f"Flag this file for manual review:\n{content}"
    return content
