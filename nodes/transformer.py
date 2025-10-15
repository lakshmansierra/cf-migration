import os
import json
import shutil
from typing import Dict
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.file_ops import read_text_file, save_dict_to_file

LLM_DEPLOYMENT_ID = "dadede28a723f679"

llm = ChatOpenAI(
    deployment_id=LLM_DEPLOYMENT_ID,
    temperature=0.2,
    base_url=os.environ.get("AICORE_BASE_URL")
)

SYSTEM_PROMPT = """
You are an expert SAP BTP migration assistant. Your task is to convert SAP Neo configuration and application files to Cloud Foundry equivalents.

Return only transformed content for CF or indicate skipped files.
"""

def transform_files(repo_root: str, plan: Dict, snippets: Dict, output_dir: str) -> Dict[str, str]:
    results = {}
    app_name = "default_app"

    # Detect app_name from neo-app.json if present
    for rel, content in snippets.items():
        if "neo-app.json" in rel and '"welcomeFile"' in content:
            try:
                app_name = json.loads(content).get("routes", [{}])[0].get("target", "default_app").split("/")[0]
            except Exception:
                app_name = "default_app"
            break

    for item in plan.get("plan", []):
        rel = item.get("file")
        action = item.get("action")
        target = (item.get("target") or "").rstrip("/\\")

        # Skip files that require manual review or have empty target
        if action in ["manual_review", "convert_mta"] or not target:
            results[rel] = f"<skipped: {action}>"
            continue

        src_path = os.path.join(repo_root, rel)
        if not os.path.exists(src_path):
            results[rel] = "<skipped: missing source>"
            continue

        # Handle directories
        if os.path.isdir(src_path):
            dest_dir = os.path.join(output_dir, target)
            os.makedirs(dest_dir, exist_ok=True)
            for root, dirs, files in os.walk(src_path):
                rel_root = os.path.relpath(root, src_path)
                current_dest = os.path.join(dest_dir, rel_root) if rel_root != "." else dest_dir
                os.makedirs(current_dest, exist_ok=True)
                for f in files:
                    shutil.copy2(os.path.join(root, f), os.path.join(current_dest, f))
            results[target] = "<directory copied>"
            continue

        # Handle file transformation
        try:
            content = read_text_file(src_path)
        except Exception:
            content = "<unreadable>"

        payload = json.dumps({
            "file_name": rel,
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

        # Write transformed file inside output_dir
        dest_path = os.path.join(output_dir, target)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(transformed_content)

        results[target] = transformed_content

    # Save summary JSON in VS Code workspace
    summary_path = os.path.join(os.getcwd(), "transform_files_output.json")
    save_dict_to_file(results, summary_path)
    print(f"\nTransformation summary saved in VS Code folder: {summary_path}")

    return results
