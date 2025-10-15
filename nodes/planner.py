import os
import json
from typing import Dict, Any, Tuple
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.file_ops import read_text_file, save_dict_to_file

# SAP AI Core Deployment ID
LLM_DEPLOYMENT_ID = "dadede28a723f679"

# Ensure environment variables
os.environ["AICORE_AUTH_URL"] = "https://gen-ai.authentication.us10.hana.ondemand.com/oauth/token"
os.environ["AICORE_CLIENT_ID"] = "sb-42a29a03-b2f4-47de-9a41-e0936be9aaf5!b256749|aicore!b164"
os.environ["AICORE_CLIENT_SECRET"] = "b5e6caee-15aa-493a-a6ac-1fef0ab6e9fe$Satg7UGYPLsz5YYeXefHpbwTfEqqCkQEbasMDPGHAgU="
os.environ["AICORE_RESOURCE_GROUP"] = "default"
os.environ["AICORE_BASE_URL"] = "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2"

# Initialize LLM
llm = ChatOpenAI(
    deployment_id=LLM_DEPLOYMENT_ID,
    temperature=0,
    base_url=os.environ.get("AICORE_BASE_URL")
)

SYSTEM_PROMPT = """
You are an expert SAP BTP migration engineer.
Your task is to inspect any given SAP Neo project and generate a complete migration plan for Cloud Foundry (CF).

Return **only valid JSON** in the following format:

{
  "plan": [
    {
      "file": "<relative path of file or directory in the Neo project>",
      "reason": "<why this file/folder requires migration or special handling>",
      "action": "<the migration action chosen by you based on file type, content, and role in the project>",
      "snippets": "<short snippet of file content (max 2000 characters) or '<directory>' for folders>",
      "target": "<target path in Cloud Foundry>"
    }
  ]
}

Rules:
1. Inspect all files and directories dynamically; do not assume any specific file names or folder structure.
2. Decide the 'action' automatically for each file or directory based on its type, purpose, and role in the Neo project.
   Valid actions include: convert_mta, convert_manifest, convert_xsapp, convert_ui5, copy_as_is, manual_review.
3. Include all files and directories relevant for migration, even if they require manual review or special handling.
4. For directories, set 'snippets' to '<directory>'.
5. 'snippets' should summarize the first few lines or first 2000 characters of content.
6. 'target' should indicate the correct Cloud Foundry deployment path.
7. Never include explanations, markdown, or text outside the JSON.
8. Ensure the plan is complete and consistent, including entries for files or folders that might not be obvious.
9. Prioritize correctness over completeness if you are unsure about a file; mark it for manual review.

Output must be **strictly parseable JSON**.
"""


def gather_repo_files(repo_dir: str, max_chars=2000):
    filenames = []
    snippets = {}

    for root, dirs, files in os.walk(repo_dir):
        for d in dirs:
            rel_path = os.path.relpath(os.path.join(root, d), repo_dir)
            filenames.append(rel_path)
            snippets[rel_path] = "<directory>"

        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), repo_dir)
            filenames.append(rel_path)
            try:
                snippets[rel_path] = read_text_file(os.path.join(root, f))[:max_chars]
            except Exception:
                snippets[rel_path] = "<unreadable>"

    return filenames, snippets

def call_llm(prompt: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    try:
        return llm.invoke(messages).content
    except Exception as e:
        return json.dumps({"error": f"llm_call_failed: {str(e)}"})

def extract_first_json(text: str) -> str:
    start = text.find("{")
    if start == -1:
        return text
    stack = []
    for i, c in enumerate(text[start:], start):
        if c == "{":
            stack.append("{")
        elif c == "}":
            stack.pop()
            if not stack:
                return text[start:i+1]
    return text[start:]

def plan_migration(repo_root: str) -> Tuple[Dict, Dict]:
    filenames, snippets = gather_repo_files(repo_root)
    repo_json = {"filenames": filenames, "snippets": snippets}
    prompt = json.dumps(repo_json, indent=2)

    #print("Planning migration...")
    plan_text = call_llm(prompt)

    cleaned_json = extract_first_json(plan_text)
    try:
        plan = json.loads(cleaned_json)
    except json.JSONDecodeError:
        plan = {"error": "failed_to_parse_plan", "raw": plan_text}
        print(" Failed to parse LLM response.")

    # Save directly in VS Code folder
    vs_code_path = os.path.abspath("plan_migration.json")
    save_dict_to_file(plan, vs_code_path)
    print(f" Migration plan saved in VS Code folder: {vs_code_path}")

    return plan, snippets