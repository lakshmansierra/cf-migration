from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
import os
import json

from utils.file_ops import prepare_output_dir, read_text_file
from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output


# State shape
class MigrationState(TypedDict, total=False):
    repo_path: str
    output_path: str
    plan: Dict[str, Any]
    transformed_files: Dict[str, str]
    written_files: Dict[str, str]


# Node functions
def planner_node(state: MigrationState) -> MigrationState:
    plan, snippets = plan_migration(state["repo_path"])
    state["plan"] = plan
    return state


def transformer_node(state: MigrationState) -> MigrationState:
    # Default app_name
    app_name = "app"

    # Try to read app_name from neo-app.json routes
    neo_app_path = os.path.join(state["repo_path"], "neo-app.json")
    if os.path.exists(neo_app_path):
        try:
            neo_app_content = read_text_file(neo_app_path)
            routes = json.loads(neo_app_content).get("routes", [])
            if routes and "target" in routes[0]:
                app_name = routes[0]["target"].split("/")[0]
        except Exception:
            app_name = "app"

    transformed = transform_files(state["repo_path"], state["plan"], app_name)
    state["transformed_files"] = transformed
    return state


def writer_node(state: MigrationState) -> MigrationState:
    output_path = prepare_output_dir(base_prefix="cf_repo_")
    written = write_output(output_path, state["repo_path"], state["transformed_files"])
    state["output_path"] = output_path
    state["written_files"] = written
    return state


# Build graph
workflow = StateGraph(MigrationState)
workflow.add_node("planner", planner_node)
workflow.add_node("transformer", transformer_node)
workflow.add_node("writer", writer_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "transformer")
workflow.add_edge("transformer", "writer")
workflow.add_edge("writer", END)

migrator_app = workflow.compile()


def run_migration(repo_path: str) -> Dict[str, Any]:
    result = migrator_app.invoke({"repo_path": repo_path})
    return result
