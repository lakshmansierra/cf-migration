from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from utils.file_ops import prepare_output_dir
from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output

class MigrationState(TypedDict, total=False):
    repo_path: str
    output_path: str
    plan: Dict[str, Any]
    transformed_files: Dict[str, str]
    written_files: Dict[str, str]

def planner_node(state: MigrationState) -> MigrationState:
    print(" Planning migration...")
    # Use existing output_path from main.py, or create one if missing
    if "output_path" not in state or not state["output_path"]:
        state["output_path"] = prepare_output_dir()
    
    plan, snippets = plan_migration(state["repo_path"], state["output_path"])
    state["plan"] = plan
    return state

def transformer_node(state: MigrationState) -> MigrationState:
    print(" Transforming files based on migration plan...")
    transformed = transform_files(state["repo_path"], state["plan"], state["output_path"])
    state["transformed_files"] = transformed
    return state

def writer_node(state: MigrationState) -> MigrationState:
    print(" Writing transformed files to destination folder...")
    written = write_output(state["output_path"], state["repo_path"], state["transformed_files"])
    state["written_files"] = written
    return state

workflow = StateGraph(MigrationState)
workflow.add_node("planner", planner_node)
workflow.add_node("transformer", transformer_node)
workflow.add_node("writer", writer_node)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "transformer")
workflow.add_edge("transformer", "writer")
workflow.add_edge("writer", END)

migrator_app = workflow.compile()

def run_migration(repo_path: str, output_path: str = None) -> Dict[str, Any]:
    state = {"repo_path": repo_path}
    if output_path:
        state["output_path"] = output_path
    result = migrator_app.invoke(state)
    print(" Migration workflow complete.\n")
    return result
