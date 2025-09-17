# neo_cf_migrator/nodes/planner.py
from typing import Dict

def plan_migration(state: Dict) -> Dict:
    repo_path = state["repo_path"]

    # For now: just say we will migrate manifest + env configs
    plan = {
        "files_to_check": ["manifest.yml", "neo-app.json", "mta.yaml"],
        "transformations": ["neo_to_cf_manifest", "env_var_update"]
    }

    state["plan"] = plan
    return state
