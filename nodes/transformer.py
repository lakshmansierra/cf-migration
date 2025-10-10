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

You will receive a JSON object with:
- file_name: relative path of the source file (string)
- action: one of [convert_xsapp, copy_as_is, manual_review]
- file_content: the content of the source file (string)

Instructions:
1. If action is `convert_xsapp`, produce the transformed Cloud Foundry equivalent of the file and return **only the file content**.
2. If action is `copy_as_is`, return the original file content unchanged.
3. If action is `manual_review` or you cannot automatically convert the file, return a JSON object like: `{"error": "<reason>"}`.
4. Maintain valid syntax for each file type (JSON, YAML, JS, XML, etc.) and preserve the original formatting as much as possible.
5. Return **strictly**:
   - Either the transformed file content, **or**
   - A small JSON error object.
6. Do not include any explanations, comments, markdown, or extra text.

Focus on correctness, CF compliance, and preserving the original functionality.
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
        target = (item.get("target") or rel).rstrip("/\\")  # remove trailing slashes
        src_path = os.path.join(repo_root, rel)
        dest_path = os.path.join(output_dir, target)

        if not os.path.exists(src_path):
            results[target] = f"#  Missing source file or folder: {rel}\n"
            continue

        #  Handle directories safely
        if os.path.isdir(src_path):
            os.makedirs(dest_path, exist_ok=True)
            for root, dirs, files in os.walk(src_path):
                rel_root = os.path.relpath(root, src_path)
                current_dest = os.path.join(dest_path, rel_root) if rel_root != "." else dest_path
                os.makedirs(current_dest, exist_ok=True)

                for f in files:
                    src_file = os.path.join(root, f)
                    dst_file = os.path.join(current_dest, f)
                    shutil.copy2(src_file, dst_file)

            results[target] = "<directory and contents copied>"
            continue  #  stop here — don’t process it as a file below

        #  Handle file transformation
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

        #  Ensure parent folder exists before writing
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # dest_path is guaranteed to be a file here
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(transformed_content)

        results[target] = transformed_content

    #  Save transformation summary
    save_dict_to_file(results, os.path.join(output_dir, "transform_files_output.json"))
    return results