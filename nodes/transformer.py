import os
import json
from typing import Dict, Any
from utils.file_ops import read_text_file, save_dict_to_file
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

LLM_DEPLOYMENT_ID = os.environ["LLM_DEPLOYMENT_ID"]
llm = ChatOpenAI(
    deployment_id=LLM_DEPLOYMENT_ID,
    temperature=0,
    base_url=os.environ["AICORE_BASE_URL"]
)

SYSTEM_PROMPT = """
You are an expert migration assistant for SAP Neo → Cloud Foundry.
Tasks:
- For each file, decide action: convert_manifest, convert_xsapp, remove_neo_route, copy_as_is, manual_review
- Suggest a **logical target path** for the output based on file type and usage
- Return transformed content if applicable, or original content for copy_as_is
- Include a short reason

Input JSON:
{
  "file_name": "<relative input path>",
  "action": "<action_type>",
  "file_content": "<original file content>"
}

Output JSON format (single object per file):
{
  "file": "<input file relative path>",
  "target": "<logical output path>",
  "action": "<action type>",
  "reason": "<short explanation>",
  "content": "<transformed or original content>"
}

Return **only JSON**.
"""

def transform_files(repo_root: str, plan: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    results: Dict[str, str] = {}
    items = plan.get("plan", [])

    for item in items:
        rel = item.get("file")
        action = item.get("action")
        src_path = os.path.join(repo_root, rel)

        if not os.path.exists(src_path):
            results[rel] = f"# MISSING SOURCE: {rel}\n"
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
            result_json = json.loads(resp.content)

            target = result_json.get("target", rel)
            results[target] = result_json.get("content", content)

        except Exception as e:
            results[rel] = json.dumps({"error": f"llm_call_failed: {str(e)}"})

    # Debug output
    output_file = Path(output_dir) / "transform_files_return.json"
    save_dict_to_file(results, str(output_file))
    return results
