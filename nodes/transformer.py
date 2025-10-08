import os
import json
from typing import Dict, Any
from utils.file_ops import read_text_file, save_dict_to_file
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from pathlib import Path

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()  # loads values from .env into os.environ

# -----------------------------
# SAP AI Core LLM setup
# -----------------------------
LLM_DEPLOYMENT_ID = os.environ["LLM_DEPLOYMENT_ID"]

llm = ChatOpenAI(
    deployment_id=LLM_DEPLOYMENT_ID,
    temperature=0,
    base_url=os.environ["AICORE_BASE_URL"]
)

# -----------------------------
# System prompt for transformer
# -----------------------------
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

# -----------------------------
# Transform files function
# -----------------------------
def transform_files(repo_root: str, plan: Dict[str, Any], output_dir: str) -> Dict[str, str]:
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

        try:
            resp = llm.invoke([HumanMessage(content=json.dumps(payload, indent=2))])
            results[target] = resp.content  # extracted transformed content
        except Exception as e:
            results[target] = json.dumps({"error": f"llm_call_failed: {str(e)}"})

    # Save debug file safely in the output_dir
    output_file = Path(output_dir) / "transform_files_return.txt"
    save_dict_to_file(results, str(output_file))
    return results
