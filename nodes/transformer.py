from typing import Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import os
import json

_llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")  # deterministic

SYSTEM_PROMPT = """
You are a migration assistant that converts SAP Neo config files to Cloud Foundry equivalents.
For each input file content and action, output the converted file content only (no extra commentary).
If you cannot convert fully, return a JSON object {"error":"explain reason"}.
"""

def transform_files(repo_root: str, plan: Dict[str, Any]) -> Dict[str, str]:
    """
    For each plan item, read the file and call the LLM to produce converted content.
    Returns mapping of target_relative_path -> transformed content.
    """
    results: Dict[str, str] = {}
    items = plan.get("plan", [])
    for item in items:
        file_rel = item.get("file")
        action = item.get("action")
        target = item.get("target") or file_rel
        src_abspath = os.path.join(repo_root, file_rel)
        if not os.path.exists(src_abspath):
            # skip missing
            continue
        try:
            with open(src_abspath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            content = ""

        # Determine prompt depending on action
        if action == "convert_manifest":
            prompt = _manifest_prompt(content, file_rel)
            transformed = _call_llm(prompt)
            results[target] = transformed
        elif action == "convert_mta":
            prompt = _mta_prompt(content, file_rel)
            transformed = _call_llm(prompt)
            results[target] = transformed
        elif action == "convert_xsapp":
            prompt = _xsapp_prompt(content, file_rel)
            transformed = _call_llm(prompt)
            results[target] = transformed
        elif action == "copy_as_is":
            results[target] = content
        elif action == "manual_review":
            # Put original content but flag for manual review by prefixing a comment
            results[target] = f"# MANUAL REVIEW REQUIRED\n{content}"
        else:
            # Default: copy as is
            results[target] = content

    return results

def _manifest_prompt(content: str, filename: str) -> str:
    return f"""
Convert this SAP Neo application routing/config ({filename}) into a Cloud Foundry manifest.yml.
Input file contents:
---
{content}
---
Produce a valid YAML manifest describing at least:
- application name (use 'migrated-app' if unknown)
- memory (256M default)
- buildpack (try to infer from files; if none, use python_buildpack)
- services list placeholders (names only)
Return only the YAML manifest content, nothing else.
"""

def _mta_prompt(content: str, filename: str) -> str:
    return f"""
Convert this mta.yaml into an equivalent Cloud Foundry manifest and notes describing service provisioning.
Input:
---
{content}
---
Return ONLY the manifest YAML for the candidate app(s).
"""

def _xsapp_prompt(content: str, filename: str) -> str:
    return f"""
Convert this xs-app.json or equivalent routing config into Cloud Foundry route definitions and manifest snippets.
Input:
---
{content}
---
Return only the transformed content.
"""

def _call_llm(prompt: str) -> str:
    sys_msg = SystemMessage(content=SYSTEM_PROMPT)
    human = HumanMessage(content=prompt)
    msg = [sys_msg, human]
    resp = _llm(msg)
    # extract content
    txt = resp.content if hasattr(resp, "content") else str(resp)
    # if LLM returns JSON with error, keep it as content for review
    return txt
