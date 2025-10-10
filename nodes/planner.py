import os
import json
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
LLM_DEPLOYMENT_ID = "dadede28a723f679"

# ------------------------
# System prompt for planner
# ------------------------
SYSTEM_PROMPT = """
You are an expert SAP BTP migration engineer.
Your task is to analyze a complete SAP Neo project structure and create a migration plan
that transforms it into an equivalent Cloud Foundry (CF) application layout.

---

### 🎯 OBJECTIVE
Generate a structured migration plan that shows:
1. What each file or folder represents in the Neo project.
2. What action should be performed to adapt or migrate it to CF.
3. Where its transformed version should exist in the CF project structure.

You must infer all CF target paths, structure, and app hierarchy automatically.
Do not rely on predefined folder names or conversion rules — decide everything yourself.

---

### 📦 EXPECTED OUTPUT
Return only a valid JSON object in the following structure:

{
  "plan": [
    {
      "file": "<original Neo relative path>",
      "reason": "<why this file exists and how it should migrate>",
      "action": "<auto-decided label such as 'transform', 'adapt', 'copy', 'ignore', 'manual_review'>",
      "snippets": "<trimmed content sample>",
      "target": "<auto-inferred Cloud Foundry target path>"
    }
  ]
}

---

### 🧠 RULES
- Analyze filenames, folder context, and snippets to infer each file’s purpose.
- Automatically design the Cloud Foundry folder layout and file destinations.
- The `"target"` field must reflect the structure you propose — create it logically.
- Avoid hardcoded examples or assumptions about CF architecture.
- If uncertain, set `"action": "manual_review"`.
- Return **only valid JSON** — no extra commentary, text, or markdown.
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
llm = ChatOpenAI(deployment_id=LLM_DEPLOYMENT_ID, temperature=0)


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

    # Build prompt dynamically
    prompt = "Here are the files in my SAP Neo project:\n"
    prompt += json.dumps(filenames, indent=2)
    prompt += "\n\nHere are short snippets from these files:\n"
    prompt += json.dumps(snippets, indent=2)
    prompt += "\n\nPlease generate a complete JSON migration plan as described in the system prompt."

    print("\n🧠 Calling SAP AI Core LLM to create migration plan...")
    ai_response = call_llm(prompt)

    # Parse JSON response
    try:
        plan = json.loads(ai_response)
        print("✅ AI returned a valid migration plan.")
    except json.JSONDecodeError:
        print("⚠️ AI returned invalid JSON. Saving raw response instead.")
        plan = {"error": "invalid_json", "raw_response": ai_response}

    save_dict_to_file(plan, os.path.join(repo_root, "plan_migration.json"))
    return plan, snippets
