import os
import json
from typing import Dict, Any, Tuple
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.file_ops import read_text_file, save_dict_to_file
 
 
# ------------------------
# SAP AI Core Credentials
# ------------------------
# Access your credentials
auth_url = os.getenv("AICORE_AUTH_URL")
client_id = os.getenv("AICORE_CLIENT_ID")
client_secret = os.getenv("AICORE_CLIENT_SECRET")
resource_group = os.getenv("AICORE_RESOURCE_GROUP")
base_url = os.getenv("AICORE_BASE_URL")
LLM_DEPLOYMENT_ID = os.getenv("LLM_DEPLOYMENT_ID")
 
# ------------------------
# System prompt for planner
# ------------------------
SYSTEM_PROMPT = """
🧠 ROLE
 
You are an expert SAP BTP Migration Engineer specializing in migrating applications from SAP Neo Environment to SAP Cloud Foundry (CF).
Your role is to deeply analyze the full Neo project structure, understand the purpose of each file and folder, and generate a complete and structured
migration plan that can guide an automated or manual transformation into Cloud Foundry.
 
🎯 OBJECTIVE
 
Your goal is to produce a comprehensive JSON migration plan that includes:
 
A precise understanding of what each file/folder represents in the Neo project.
 
A recommended migration action for that file/folder (e.g., transform, copy, ignore, or manual review).
 
The target location and structure in the new Cloud Foundry layout, inferred intelligently based on the file’s purpose and context.
 
The output should reflect a complete Cloud Foundry project design, created logically and automatically — not based on fixed templates or assumptions.
 
📦 EXPECTED OUTPUT FORMAT
 
Return only a valid JSON object in the exact format below:
 
{
  "plan": [
    {
      "file": "<original Neo relative path>",
      "reason": "<explain what this file does in Neo and why it needs migration or adaptation>",
      "action": "<one of: transform | adapt | copy | ignore | manual_review>",
      "snippets": "<short trimmed sample of content to support your reasoning>",
      "target": "<auto-inferred target path in the new Cloud Foundry layout>"
    }
  ]
}
 
⚙️ DETAILED INSTRUCTIONS
🔍 1. Analysis Guidelines
 
Examine file names, extensions, folder hierarchy, and short content snippets.
 
Use contextual reasoning to infer each file’s purpose in the Neo application (e.g., UI module, backend service, configuration, security descriptor, etc.).
 
Identify whether the file is:
 
Source code (e.g., java application, hana xs, HTML application)
 
Configuration (e.g., .json, .yaml, .xsapp, .mta, manifest.yml)
 
Resource or asset (e.g., .html, .css, .xml, .properties)
 
Deployment or infrastructure metadata.
 
⚒️ 2. Action Decision Rules
 
Decide the appropriate "action" for each file:
 
Action  Meaning
transform   Requires modification to CF format or syntax (e.g., neo-app.json → manifest.yml).
adapt   Needs slight refactoring to align with CF APIs or environment variables.
copy    Can be reused directly in CF with minimal or no change.
ignore  Not needed in CF (obsolete or irrelevant files).
manual_review   Unclear purpose or requires human inspection before migration.
🗂️ 3. CF Target Structure Inference
 
Create the Cloud Foundry folder structure dynamically based on logical grouping and app purpose.
 
Infer where files belong in CF:
 
Application source → app/, srv/, or modules/
 
Config files → root level or config/
 
UI content → resources/, static/, or webapp/
 
Service bindings and environment variables → manifest.yml or mta.yaml
 
Avoid hardcoded or generic folder names. Derive the structure naturally from the Neo project context.
 
🧩 4. Snippet Extraction
 
Include a short content preview (first few meaningful lines) in "snippets" to show the reasoning base.
Trim unnecessary code or sensitive data — just enough to demonstrate context.
 
🚫 RESTRICTIONS
 
Output only valid JSON — no explanations, markdown, or commentary.
 
No placeholder text such as “example path” or “sample reason.”
 
Do not assume pre-defined CF folder structures; always infer from the given Neo project.
 
If uncertain about a file’s role, set "action": "manual_review" and clearly state the reason.
 
✅ Your goal: Produce a clean, structured, and logically inferred JSON migration plan that accurately reflects how the Neo project should be restructured for Cloud Foundry.
No extra explanations, no markdown, only valid JSON.
 
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
    



    # # Save the function's output to a file
    # output = plan_migration()
    # with open("planner.txt", "w") as file:
    #     file.write(output)   
    
    # Parse JSON response
    try:
        plan = json.loads(ai_response)
        print("✅ AI returned a valid migration plan.")
    except json.JSONDecodeError:
        print("⚠️ AI returned invalid JSON. Saving raw response instead.")
        plan = {"error": "invalid_json", "raw_response": ai_response}
 
    save_dict_to_file(plan, os.path.join(repo_root, "plan_migration.json"))
    return plan, snippets