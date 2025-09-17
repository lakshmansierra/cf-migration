# neo_cf_migrator/graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict

from nodes.planner import plan_migration
from nodes.transformer import transform_files
from nodes.writer import write_output

# Shared state
class MigrationState(TypedDict):
    repo_path: str
    plan: dict
    transformed_files: dict
    output_path: str

def build_graph():
    graph = StateGraph(MigrationState)

    # Nodes
    graph.add_node("planner", plan_migration)
    graph.add_node("transformer", transform_files)
    graph.add_node("writer", write_output)

    # Flow
    graph.set_entry_point("planner")
    graph.add_edge("planner", "transformer")
    graph.add_edge("transformer", "writer")
    graph.add_edge("writer", END)

    return graph.compile()
