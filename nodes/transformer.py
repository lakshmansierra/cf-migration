import os
import json
import requests
from typing import Dict, Any
from utils.file_ops import read_text_file, save_dict_to_file

from langchain.schema import HumanMessage  # kept for compatibility if you build prompts similarly

# === SAP AI Core Credentials and endpoints (from user) ===
AICORE_AUTH_URL = "https://gen-ai.authentication.us10.hana.ondemand.com/"  # ensure trailing slash
AICORE_CLIENT_ID = "sb-42a29a03-b2f4-47de-9a41-e0936be9aaf5!b256749|aicore!b164"
AICORE_CLIENT_SECRET = "b5e6caee-15aa-493a-a6ac-1fef0ab6e9fe$Satg7UGYPLsz5YYeXefHpbwTfEqqCkQEbasMDPGHAgU="
AICORE_RESOURCE_GROUP = "default"

DEPLOYMENT_URL = "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/d6d36c0e481318cf/models/gemini-1.5-flash:generateContent%22"

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

def _get_access_token() -> str:
    token_url = AICORE_AUTH_URL.rstrip("/") + "/oauth/token"
    resp = requests.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=(AICORE_CLIENT_ID, AICORE_CLIENT_SECRET),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("access_token")

def _call_sap_ai_core(prompt: str) -> str:
    try:
        token = _get_access_token()
    except Exception as e:
        return json.dumps({"error": f"auth_failed: {str(e)}"})

    headers = {
        "AI-Resource-Group": AICORE_RESOURCE_GROUP,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "input": prompt
    }

    try:
        r = requests.post(DEPLOYMENT_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        resp_json = r.json()
    except Exception as e:
        return json.dumps({"error": f"inference_call_failed: {str(e)}"})

    # best-effort extraction (same logic as planner)
    try:
        if isinstance(resp_json, dict) and "candidates" in resp_json:
            c0 = resp_json["candidates"][0]
            content = c0.get("content", {})
            parts = content.get("parts") or content.get("textParts")
            if isinstance(parts, list) and parts:
                p = parts[0]
                if isinstance(p, dict) and "text" in p:
                    return p["text"]
                elif isinstance(p, str):
                    return p
            if isinstance(content, dict) and "text" in content:
                return content["text"]

        if isinstance(resp_json, dict) and "outputs" in resp_json:
            outputs = resp_json["outputs"]
            if isinstance(outputs, list) and outputs:
                o = outputs[0]
                cont = o.get("content")
                if isinstance(cont, dict) and "text" in cont:
                    return cont["text"]
                if isinstance(cont, str):
                    return cont

        for key in ("text", "result", "prediction", "output"):
            if isinstance(resp_json, dict) and key in resp_json:
                v = resp_json[key]
                if isinstance(v, str):
                    return v

        return json.dumps(resp_json)
    except Exception:
        return json.dumps(resp_json)

# --- Transform files based on migration plan ---
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

        resp = _call_sap_ai_core(prompt)
        results[target] = resp

    save_dict_to_file(results, "transform_files_return.txt")
    return results
