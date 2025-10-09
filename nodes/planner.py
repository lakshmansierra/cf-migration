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
    # 1️⃣ Read all filenames and short file contents (snippets)
    filenames, snippets = gather_repo_files(repo_root)

    # 2️⃣ Build the AI prompt dynamically based on project files
    prompt = "Here are the files in my SAP Neo project:\n"
    prompt += json.dumps(filenames, indent=2)
    prompt += "\n\nHere are short snippets from these files:\n"
    prompt += json.dumps(snippets, indent=2)
    prompt += "\n\nPlease produce a JSON migration plan as described in the system prompt."

    # 3️⃣ Ask the AI to generate the migration plan
    print("\n🧠 Calling SAP AI Core LLM to create migration plan...")
    ai_response = call_llm(prompt)

    # 4️⃣ Parse the AI's response (string → Python dict)
    try:
        plan = json.loads(ai_response)
        print("✅ AI returned a valid migration plan.")
    except json.JSONDecodeError:
        print("⚠️ AI returned invalid JSON. Saving raw response instead.")
        plan = {"error": "invalid_json", "raw_response": ai_response}

    # 5️⃣ Save the AI-generated plan for reference
    save_dict_to_file(plan, os.path.join(repo_root, "plan_migration.json"))

    # 6️⃣ Return the AI-generated plan and snippets
    return plan, snippets
