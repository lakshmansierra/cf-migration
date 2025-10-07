import os
import json
import re
from typing import Dict, Any, Tuple
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from utils.file_ops import read_text_file, save_dict_to_file


# ------------------------
# SAP AI Core Credentials
# ------------------------
os.environ["AICORE_AUTH_URL"] = "https://gen-ai.authentication.us10.hana.ondemand.com/oauth/token"
os.environ["AICORE_CLIENT_ID"] = "sb-42a29a03-b2f4-47de-9a41-e0936be9aaf5!b256749|aicore!b164"
os.environ["AICORE_CLIENT_SECRET"] = "b5e6caee-15aa-493a-a6ac-1fef0ab6e9fe$Satg7UGYPLsz5YYeXefHpbwTfEqqCkQEbasMDPGHAgU="
os.environ["AICORE_RESOURCE_GROUP"] = "default"
os.environ["AICORE_BASE_URL"] = "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2"

# --- Model Deployment ---
LLM_DEPLOYMENT_ID = "dadede28a723f679"  # ✅ Replace with your actual Gemini-2.5-pro deployment if needed

# ------------------------
# System prompt for planner
# ------------------------
SYSTEM_PROMPT = """
You are a senior SAP BTP migration engineer.
Inspect a SAP Neo project and produce a migration plan to Cloud Foundry (CF)
using Managed Approuter + HTML5 Application Repository.

Return JSON of the form:
{
  "plan": [
    {
      "file": "<Neo relative path>",
      "reason": "<why this action>",
      "action": "<convert_mta, convert_manifest, convert_xsapp, convert_ui5, copy_as_is, manual_review>",
      "snippets": "<file content or first few lines>",
      "target": "<CF target path>"
    }
  ]
}
Return only valid JSON, nothing else.
"""

# ------------------------
# Gather repo files
# ------------------------
def gather_repo_files(repo_dir: str, max_chars=2000) -> Tuple[list, dict]:
    filenames = []
    snippets = {}
    for root, _, files in os.walk(repo_dir):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), repo_dir)
            filenames.append(rel_path)
            try:
                snippets[rel_path] = read_text_file(os.path.join(root, f))[:max_chars]
            except Exception:
                snippets[rel_path] = "<unreadable>"
    return filenames, snippets


# ------------------------
# Initialize LLM
# ------------------------
llm = ChatOpenAI(
    deployment_id=LLM_DEPLOYMENT_ID,
    temperature=0,
)


# ------------------------
# Call LLM via SAP AI Core
# ------------------------
def call_llm(prompt: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return json.dumps({"error": f"llm_call_failed: {str(e)}"})


# ------------------------
# Generate Migration Plan
# ------------------------
def plan_migration(repo_root: str) -> Tuple[dict, dict]:
    filenames, snippets = gather_repo_files(repo_root)
    repo_json = {"filenames": filenames, "snippets": snippets}
    prompt = json.dumps(repo_json, indent=2)

    plan_text = call_llm(prompt)

    # --- Clean and parse JSON from model output ---
    try:
        # Try to extract only the JSON portion if extra text is around it
        match = re.search(r'\{[\s\S]*\}', plan_text)
        if match:
            cleaned_json = match.group(0)
        else:
            cleaned_json = plan_text

        plan = json.loads(cleaned_json)
    except Exception as e:
        plan = {"error": "failed_to_parse_plan", "raw": plan_text}
        print(f"⚠️ Failed to parse model response: {e}")

    # Save output for debugging
    save_dict_to_file(plan, os.path.join(repo_root, "plan_migration.json"))

    return plan, snippets
