import os
from typing import Dict, Any
from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client("gen-ai-hub")
llm = GenerativeModel(
    deployment_id=os.getenv("MODEL_DEPLOYMENT_ID"),
    model_name=os.getenv("MODEL_NAME"),
    proxy_client=proxy_client
)

SYSTEM_PROMPT = """
You are a migration assistant that converts SAP Neo config files to Cloud Foundry equivalents.
For each input file content and action, output only the converted file content.
If you cannot convert fully, return {"error":"reason"}.
"""

def transform_files(repo_root: str, plan: Dict[str, Any]) -> Dict[str, str]:
    results = {}
    items = plan.get("plan", [])
    for item in items:
        file_rel = item.get("file")
        target = item.get("target") or file_rel
        src_abspath = os.path.join(repo_root, file_rel)
        if not os.path.exists(src_abspath):
            continue
        with open(src_abspath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        payload = {
            "file_content": content,
            "file_name": file_rel,
            "action": item.get("action"),
            "instructions": SYSTEM_PROMPT
        }

        resp = llm.generate(payload)
        transformed = resp.get("content", content) if isinstance(resp, dict) else content
        results[target] = transformed
    return results
