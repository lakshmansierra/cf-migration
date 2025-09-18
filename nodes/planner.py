from typing import Dict, Any, List
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import os
import json

# Configure LLM here (temperature 0 for deterministic outputs)
_llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")  # change model name if needed

SYSTEM_PROMPT = """
You are an expert assistant that detects which files in an SAP Neo application repository must be migrated to run on SAP Cloud Foundry.
Output a JSON object with a single key "plan" whose value is a list of objects with:
- file: relative path (string)
- reason: short reason (string)
- action: one of ["convert_manifest", "remove_neo_route", "convert_mta", "convert_xsapp", "copy_as_is", "manual_review"]
- target: suggested target filename if action creates new file (or null)
Return only valid JSON.
"""

def plan_migration(repo_root: str) -> Dict[str, Any]:
    """
    Inspect the repo (file list, basic content) and ask LLM which files to transform and how.
    Returns a plan dict: {'plan': [ {file, reason, action, target}, ... ] }
    """
    # gather some contextual filenames and small file snippets
    filenames = []
    snippets = {}
    for root, _, files in os.walk(repo_root):
        for fn in files:
            filenames.append(os.path.join(root, fn))
    # convert to relative for readability
    rel_files = [os.path.relpath(f, repo_root) for f in filenames][:400]  # limit length

    # include a few relevant file contents (neo-app.json, mta.yaml, xs-app.json, xs-security.json)
    interesting = ["neo-app.json", "mta.yaml", "xs-app.json", "xs-security.json", "manifest.yml"]
    for f in filenames:
        if os.path.basename(f) in interesting:
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                    snippets[os.path.relpath(f, repo_root)] = fh.read()[:4000]
            except Exception:
                snippets[os.path.relpath(f, repo_root)] = "<unreadable>"

    # build prompt
    payload = {
        "filenames": rel_files[:200],
        "snippets": snippets
    }

    human = HumanMessage(
        content=f"""
Repo context (JSON): {json.dumps(payload, indent=2)}
Based on the repo context, produce a migration plan (JSON) describing which files to convert and how.
Remember to return only JSON with key "plan".
"""
    )

    msg = [_make_system(), human]
    resp = _llm(msg)
    text = resp.content.strip()

    # Try to parse JSON - if LLM returns raw JSON, parse safely
    import json
    try:
        parsed = json.loads(text)
    except Exception:
        # fallback: attempt to find the first JSON object substring
        import re
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            parsed = json.loads(m.group(0))
        else:
            # fallback rule-based simple plan: look for neo-app.json and mta.yaml
            parsed = {"plan": []}
            if any("neo-app.json" in rf for rf in rel_files):
                parsed["plan"].append({
                    "file": "neo-app.json",
                    "reason": "Contains Neo routing and application configuration",
                    "action": "convert_manifest",
                    "target": "manifest.yml"
                })
            if any("mta.yaml" in rf for rf in rel_files):
                parsed["plan"].append({
                    "file": "mta.yaml",
                    "reason": "MTA descriptor present",
                    "action": "convert_mta",
                    "target": "mta.yaml"
                })
    return parsed

def _make_system() -> SystemMessage:
    return SystemMessage(content=SYSTEM_PROMPT)

def _llm(messages):
    # wrapper to call the ChatOpenAI model in a compatible way
    return _llm.infer_messages(messages) if hasattr(_llm, "infer_messages") else _llm(messages)
