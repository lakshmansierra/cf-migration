import os
import json
from typing import Dict, Any
from utils.file_ops import read_text_file, save_dict_to_file

from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
from langchain.schema import HumanMessage
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

# === Hardcoded SAP AI Core client ===
AICORE_CLIENT = AICoreV2Client(
    base_url="https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2",  # ✅ only base URL
    auth_url="https://gen-ai.authentication.us10.hana.ondemand.com/oauth/token",
    client_id="sb-42a29a03-b2f4-47de-9a41-e0936be9aaf5!b256749|aicore!b164",
    client_secret="b5e6caee-15aa-493a-a6ac-1fef0ab6e9fe$Satg7UGYPLsz5YYeXefHpbwTfEqqCkQEbasMDPGHAgU=",
    resource_group="default",
)

LLM_DEPLOYMENT_ID = "dda84494ee46f575"
MODEL_NAME = "gemini-2.5-pro"

# === System prompt ===
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

# --- Call Gemini on SAP AI Core ---
def _call_sap_ai_core(prompt: str) -> str:
    model = GenerativeModel(
        deployment_id=LLM_DEPLOYMENT_ID,
        model=MODEL_NAME,
        aicore_proxy_client=AICORE_CLIENT,
    )
    message = HumanMessage(content=prompt)
    response = model.generate_content([message])

    if hasattr(response, "candidates") and response.candidates:
        parts = response.candidates[0].content.parts
        if parts and hasattr(parts[0], "text"):
            return parts[0].text
    return ""

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
