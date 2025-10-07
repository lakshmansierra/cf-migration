import os
import json
from typing import Dict, Any
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from utils.file_ops import read_text_file, save_dict_to_file

# ------------------------
# SAP AI Core Credentials
# ------------------------
# --- SAP AI Core Credentials ---
os.environ["AICORE_AUTH_URL"] = "https://gen-ai.authentication.us10.hana.ondemand.com/oauth/token"
os.environ["AICORE_CLIENT_ID"] = "sb-42a29a03-b2f4-47de-9a41-e0936be9aaf5!b256749|aicore!b164"
os.environ["AICORE_CLIENT_SECRET"] = "b5e6caee-15aa-493a-a6ac-1fef0ab6e9fe$Satg7UGYPLsz5YYeXefHpbwTfEqqCkQEbasMDPGHAgU="
os.environ["AICORE_RESOURCE_GROUP"] = "default"
os.environ["AICORE_BASE_URL"] = "https://api.ai.prod.us-east-1.aws.ml.hana.ondemand.com/v2"  # ✅ no comma!

# --- Model Deployment ---
LLM_DEPLOYMENT_ID = "dadede28a723f679"
SYSTEM_PROMPT = """You are a senior SAP BTP migration engineer.
Convert SAP Neo config files and artifacts to Cloud Foundry equivalents using Managed Approuter + HTML5 Application Repository.

# INPUT
You will receive JSON containing:
- file_name: relative path
- action: one of [convert_manifest, convert_mta, convert_xsapp, convert_ui5, copy_as_is, manual_review]
- file_content: original Neo content
- app_name: the derived application name from neo-app.json

# RULES
- neo-app.json → apps/<APP_NAME>/xs-app.json (routes + welcomeFile)
- manifest.yml / mta.yaml → CF mta.yaml with approuter, html5 modules, deployer, xsuaa, destinations
- xs-security.json → xs-security.json for CF
- UI5 app → apps/<APP_NAME>/package.json + ui5.yaml
- copy_as_is → keep original
- If unable to convert → return {"error": "<reason>"}

# OUTPUT
Return ONLY the transformed file content (JSON/YAML/text), do not wrap in explanations.
"""

# ------------------------
# Initialize LLM
# ------------------------
llm = ChatOpenAI(deployment_id=LLM_DEPLOYMENT_ID, temperature=0.2)

# ------------------------
# Transform files
# ------------------------
def transform_files(repo_root: str, plan: Dict[str, Any], app_name: str) -> Dict[str, str]:
    results: Dict[str, str] = {}
    items = plan.get("plan", [])

    for item in items:
        src_rel = item["file"]
        target_rel = item["target"]
        action = item["action"]
        src_path = os.path.join(repo_root, src_rel)

        if not os.path.exists(src_path):
            results[target_rel] = f"# MISSING SOURCE: {src_rel}\n"
            continue

        content = read_text_file(src_path)
        payload = json.dumps({
            "file_name": src_rel,
            "action": action,
            "file_content": content,
            "app_name": app_name
        }, indent=2)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=payload)
        ]
        try:
            transformed_content = llm.invoke(messages).content
        except Exception as e:
            transformed_content = json.dumps({"error": f"llm_call_failed: {str(e)}"})

        results[target_rel] = transformed_content

    save_dict_to_file(results, os.path.join(repo_root, "transform_files_return.json"))
    return results

def save_transformed_files(transformed: Dict[str, str], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for rel_path, content in transformed.items():
        out_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)