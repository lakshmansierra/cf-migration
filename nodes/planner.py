import os, json
from typing import Dict, Any
from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

# Load LLM through AI Core
proxy_client = get_proxy_client("gen-ai-hub")
llm = GenerativeModel(
    deployment_id=os.getenv("MODEL_DEPLOYMENT_ID"),
    model_name=os.getenv("MODEL_NAME"),
    proxy_client=proxy_client
)

SYSTEM_PROMPT = """
You are an expert assistant that detects which files in an SAP Neo application repository must be migrated to run on SAP Cloud Foundry.
Output a JSON object with a single key "plan" whose value is a list of objects with:
- file: relative path (string)
- reason: short reason (string)
- action: one of ["convert_manifest", "remove_neo_route", "convert_mta", "convert_xsapp", "copy_as_is", "manual_review"]
- target: suggested target filename if action creates new file (or null)
Return only valid JSON.
"""

def plan_migration(repo_root: str) -> Dict[str, Any]:
    # gather file paths
    filenames, snippets = [], {}
    for root, _, files in os.walk(repo_root):
        for f in files:
            filenames.append(os.path.join(root, f))
    rel_files = [os.path.relpath(f, repo_root) for f in filenames][:400]

    interesting = ["neo-app.json", "mta.yaml", "xs-app.json", "xs-security.json", "manifest.yml"]
    for f in filenames:
        if os.path.basename(f) in interesting:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    snippets[os.path.relpath(f, repo_root)] = fh.read()[:4000]
            except:
                snippets[os.path.relpath(f, repo_root)] = "<unreadable>"

    payload = {
        "filenames": rel_files[:200],
        "snippets": snippets,
        "instructions": SYSTEM_PROMPT
    }

    resp = llm.generate(payload)  # call AI Core
    text = resp.get("content", "") if isinstance(resp, dict) else str(resp)
    try:
        return json.loads(text)
    except:
        return {"plan": []}  # fallback empty plan
