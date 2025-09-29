import os
import json
import requests
from typing import Dict, Any, List
from utils.file_ops import read_text_file, save_dict_to_file

from langchain.schema import HumanMessage  # kept for compatibility with existing prompt usage

# === SAP AI Core Credentials and endpoints (from user) ===
AICORE_AUTH_URL = "https://gen-ai.authentication.us10.hana.ondemand.com/"  # ensure trailing slash
AICORE_CLIENT_ID = "sb-42a29a03-b2f4-47de-9a41-e0936be9aaf5!b256749|aicore!b164"
AICORE_CLIENT_SECRET = "b5e6caee-15aa-493a-a6ac-1fef0ab6e9fe$Satg7UGYPLsz5YYeXefHpbwTfEqqCkQEbasMDPGHAgU="
AICORE_RESOURCE_GROUP = "default"

# Replace with the deployment URL you provided (quoted string)
DEPLOYMENT_URL = "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2/inference/deployments/d6d36c0e481318cf/models/gemini-1.5-flash:generateContent%22"

# === System instructions ===
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
                snippets[rel] = read_text_file(os.path.join(repo_root, rel))
            except:
                snippets[rel] = "<unreadable>"
            count += 1
    # print(snippets,"&&&&&")      
    x = {"filenames": filenames, "snippets": snippets}
    print(x)  
    return x

# --- Authenticate and call SAP AI Core deployment via HTTP ---
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
    """
    Authenticate with SAP AI Core using client credentials and call the given deployment URL.
    Returns the best-effort extracted text from the model response.
    """
    try:
        token = _get_access_token()
    except Exception as e:
        return json.dumps({"error": f"auth_failed: {str(e)}"})

    headers = {
        "AI-Resource-Group": AICORE_RESOURCE_GROUP,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # Minimal generic payload — adjust if your deployment expects a different schema.
    payload = {
        "input": prompt
    }

    try:
        r = requests.post(DEPLOYMENT_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        resp_json = r.json()
    except Exception as e:
        return json.dumps({"error": f"inference_call_failed: {str(e)}"})

    # Try to extract common response shapes:
    # - { "candidates": [ { "content": { "parts": [{"text": "..." }] } } ] }
    # - { "outputs": [{"content": {"text": "..."}}] }
    # - { "predictions" / "result" / raw text }
    try:
        # path 1: candidates -> content -> parts -> text
        if isinstance(resp_json, dict) and "candidates" in resp_json:
            c0 = resp_json["candidates"][0]
            # drill down
            text = None
            if isinstance(c0, dict):
                content = c0.get("content", {})
                parts = content.get("parts") or content.get("textParts")
                if isinstance(parts, list) and parts:
                    p = parts[0]
                    if isinstance(p, dict) and "text" in p:
                        text = p["text"]
                    elif isinstance(p, str):
                        text = p
                elif isinstance(content, dict) and "text" in content:
                    text = content["text"]
            if text:
                return text

        # path 2: outputs list
        if isinstance(resp_json, dict) and "outputs" in resp_json:
            outputs = resp_json["outputs"]
            if isinstance(outputs, list) and outputs:
                o = outputs[0]
                if isinstance(o, dict) and "content" in o:
                    cont = o["content"]
                    if isinstance(cont, dict) and "text" in cont:
                        return cont["text"]
                    # sometimes content may be a flat string
                    if isinstance(cont, str):
                        return cont

        # path 3: direct text fields
        for key in ("text", "result", "prediction", "output"):
            if isinstance(resp_json, dict) and key in resp_json:
                v = resp_json[key]
                if isinstance(v, str):
                    return v

        # fallback: return a compact JSON string (so caller can parse)
        return json.dumps(resp_json)
    except Exception:
        return json.dumps(resp_json)

def plan_migration(repo_root: str) -> Dict[str, Any]:
    payload = _gather(repo_root)
    save_dict_to_file(payload, os.path.join(repo_root, "_gather_return.txt"))

    prompt_obj = {
        "instructions": SYSTEM_INSTRUCTIONS,
        "filenames": payload["filenames"],
        "snippets": payload["snippets"]
    }
    prompt = json.dumps(prompt_obj, indent=2)

    resp = _call_sap_ai_core(prompt)
    try:
        parsed = json.loads(resp) if isinstance(resp, str) else resp
        if "plan" in parsed and isinstance(parsed["plan"], list):
            save_dict_to_file(parsed, "plan_migration_return.txt")  # save only valid plan
            return parsed
    except Exception:
        pass

    return {"plan": []}
