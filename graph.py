from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END

from utils.file_ops import prepare_output_dir
from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output


# Define state shape
class MigrationState(TypedDict, total=False):
    repo_path: str
    output_path: str
    plan: Dict[str, Any]
    transformed_files: Dict[str, str]
    written_files: Dict[str, str]


# --- Node functions ---
def planner_node(state: MigrationState) -> MigrationState:
    plan = plan_migration(state["repo_path"])
    state["plan"] = plan
    return state


def transformer_node(state: MigrationState) -> MigrationState:
    transformed = transform_files(state["repo_path"], state["plan"])
    state["transformed_files"] = transformed
    return state


def writer_node(state: MigrationState) -> MigrationState:
    output_path = prepare_output_dir()
    written = write_output(output_path, state["repo_path"], state["transformed_files"])
    state["output_path"] = output_path
    state["written_files"] = written
    return state


# --- Build graph ---
workflow = StateGraph(MigrationState)

workflow.add_node("planner", planner_node)
workflow.add_node("transformer", transformer_node)
workflow.add_node("writer", writer_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "transformer")
workflow.add_edge("transformer", "writer")
workflow.add_edge("writer", END)

# Compile the graph into an app
migrator_app = workflow.compile()


def run_migration(repo_path: str) -> Dict[str, Any]:
    """Run the migration workflow."""
    result = migrator_app.invoke({"repo_path": repo_path})
    return result
