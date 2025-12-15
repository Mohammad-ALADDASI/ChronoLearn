"""
graph_builder.py
-------------------
Converts validated triples into a directed NetworkX knowledge graph.

Each triple:
{
    "subject": "...",
    "predicate": "...",
    "object": "...",
    "span": "..."
}

Produces:
- nodes for subjects + objects
- directed edges for predicates
- metadata: theme, tbox, span

This module is independent of visualization.
"""

import networkx as nx
from typing import List, Dict, Any


# ------------------------------------------------------
# Utility: Normalize and sanitize labels
# ------------------------------------------------------
def normalize_label(label: str) -> str:
    """
    Normalize entity labels (Arabic/English).
    Remove trailing spaces, unify internal spacing.
    """
    return " ".join(label.split()).strip()


# ------------------------------------------------------
# Add a single triple to a graph
# ------------------------------------------------------
def add_triple(
    G: nx.DiGraph,
    triple: Dict[str, Any],
    theme: str = "",
    tbox: str = "",
    source_file: str = ""
):
    """
    Inserts subject, object and predicate edge into the graph.
    Applies styling metadata to nodes and edges.
    """

    subject = normalize_label(triple["subject"])
    predicate = normalize_label(triple["predicate"])
    object_ = normalize_label(triple["object"])
    span = triple.get("span", "")

    # Add nodes
    if subject not in G:
        G.add_node(
            subject,
            label=subject,
            theme=theme,
            tbox=tbox,
            source=source_file,
            type="entity"
        )

    if object_ not in G:
        G.add_node(
            object_,
            label=object_,
            theme=theme,
            tbox=tbox,
            source=source_file,
            type="entity"
        )

    # Add edge (semantic relation)
    G.add_edge(
        subject,
        object_,
        label=predicate,
        predicate=predicate,
        theme=theme,
        tbox=tbox,
        span=span,
        source=source_file
    )


# ------------------------------------------------------
# Build a graph from a list of triples
# ------------------------------------------------------
def build_graph_from_triples(
    triples: List[Dict[str, Any]],
    theme: str,
    tbox: str,
    source_file: str = ""
) -> nx.DiGraph:
    """
    Creates a new graph from triples.
    """

    G = nx.DiGraph()

    for t in triples:
        add_triple(G, t, theme, tbox, source_file)

    return G


# ------------------------------------------------------
# Merge multiple triple graphs
# ------------------------------------------------------
def merge_graphs(graphs: List[nx.DiGraph]) -> nx.DiGraph:
    """
    Combines multiple NetworkX graphs into one.
    """

    G = nx.DiGraph()

    for g in graphs:
        for node, attrs in g.nodes(data=True):
            if node not in G:
                G.add_node(node, **attrs)
            else:
                # Merge metadata if needed
                G.nodes[node].update(attrs)

        for u, v, attrs in g.edges(data=True):
            if not G.has_edge(u, v):
                G.add_edge(u, v, **attrs)
            else:
                # Merge edge metadata
                G.edges[u, v].update(attrs)

    return G


# ------------------------------------------------------
# Export NetworkX Graph
# ------------------------------------------------------
def export_graph(
    G: nx.DiGraph,
    folder: str = "triples/",
    basename: str = "kg_graph"
) -> dict:
    """
    Save graph in multiple formats:
    - GEXF (Gephi)
    - GraphML

    Returns dict of saved paths.
    """

    import os
    os.makedirs(folder, exist_ok=True)

    paths = {}

    gexf_path = os.path.join(folder, f"{basename}.gexf")
    nx.write_gexf(G, gexf_path, encoding="utf-8")
    paths["gexf"] = gexf_path

    graphml_path = os.path.join(folder, f"{basename}.graphml")
    nx.write_graphml(G, graphml_path, encoding="utf-8")
    paths["graphml"] = graphml_path

    return paths


# ------------------------------------------------------
# Module Test
# ------------------------------------------------------
if __name__ == "__main__":
    triples = [
        {
            "subject": "مؤتمر المناخ العالمي",
            "predicate": "عقد في",
            "object": "باريس",
            "span": "انعقد مؤتمر المناخ العالمي في باريس."
        },
        {
            "subject": "خبراء",
            "predicate": "شارك في",
            "object": "مؤتمر المناخ العالمي",
            "span": "شارك خبراء في المؤتمر."
        }
    ]

    theme = "event"
    tbox = "dbo:Event"

    G = build_graph_from_triples(triples, theme, tbox, source_file="report.pdf")

    print("Nodes:", G.nodes(data=True))
    print("Edges:", G.edges(data=True))

    paths = export_graph(G)
    print("Graph exported:", paths)
