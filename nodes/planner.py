import os
import json
import re
from typing import Dict, Any, Tuple, List
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.file_ops import read_text_file, save_dict_to_file
from dotenv import load_dotenv

load_dotenv()

# SAP AI Core LLM setup
LLM_DEPLOYMENT_ID = os.environ["LLM_DEPLOYMENT_ID"]
llm = ChatOpenAI(
    deployment_id=LLM_DEPLOYMENT_ID,
    temperature=0,
    base_url=os.environ["AICORE_BASE_URL"]
)


# LLM Instructions
SYSTEM_INSTRUCTIONS = """
You are an expert assistant that inspects a repository layout for an SAP Neo application 
and produces a migration plan for Cloud Foundry deployment.

Tasks:
1. Decide which files are relevant for migration.
2. Suggest an action for each file: convert_manifest, remove_neo_route, convert_mta, convert_xsapp, copy_as_is, manual_review
3. Provide a short reason.
4. Optionally suggest a target filename.

Input (JSON):
* filenames: list of relative file paths
* snippets: mapping of relpath -> small snippet of file content

Output JSON:
{
  "plan": [
    {
      "file": "<relative/path/to/file>",
      "reason": "<short reason>",
      "action": "<one of convert_manifest, remove_neo_route, convert_mta, convert_xsapp, copy_as_is, manual_review>",
      "target": "<suggested target filename or null>",
      "snippet": "<snippet of the file>"
    }
  ]
}
Return only valid JSON.
"""

# Helper: gather repo files
def gather_repo_files(repo_root: str, max_files: int = 400, max_snippets: int = 50) -> Dict[str, Any]:
    filenames: List[str] = []
    snippets: Dict[str, str] = {}

    for root, _, files in os.walk(repo_root):
        for f in files:
            filenames.append(os.path.relpath(os.path.join(root, f), repo_root))
    filenames = sorted(filenames)[:max_files]

    interesting_files = {"neo-app.json", "mta.yaml", "mta.yml", "xs-security.json", "manifest.yml", "package.json"}
    count = 0
    for rel in filenames:
        if os.path.basename(rel) in interesting_files and count < max_snippets:
            try:
                snippets[rel] = read_text_file(os.path.join(repo_root, rel))
            except Exception:
                snippets[rel] = "<unreadable>"
            count += 1

    return {"filenames": filenames, "snippets": snippets}


# Plan migration
def plan_migration(repo_root: str, output_dir: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    payload = gather_repo_files(repo_root)
    save_dict_to_file(payload, os.path.join(output_dir, "_gather_return.json"))

    prompt_content = json.dumps(payload, indent=2)
    messages = [
        SystemMessage(content=SYSTEM_INSTRUCTIONS),
        HumanMessage(content=prompt_content)
    ]

    try:
        response = llm.invoke(messages)
        plan_text = response.content
    except Exception as e:
        plan_text = json.dumps({"error": f"llm_call_failed: {str(e)}"})
        print(f" LLM call failed: {e}")

    try:
        match = re.search(r'\{[\s\S]*\}', plan_text)
        plan = json.loads(match.group(0) if match else plan_text)
    except Exception as e:
        plan = {"error": "failed_to_parse_plan", "raw": plan_text}
        print(f" Failed to parse model response: {e}")

    save_dict_to_file(plan, os.path.join(output_dir, "plan_migration.json"))
    return plan, payload.get("snippets", {})
