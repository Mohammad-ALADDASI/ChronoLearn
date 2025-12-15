"""
graph_visualiser.py
-----------------------
Visualizes a semantic knowledge graph (NetworkX DiGraph) using PyVis.

Features:
- Arabic + English font support
- Node coloring by theme or T-Box class
- Predicate-labeled edges
- Tooltip metadata (span, source file)
- Browser auto-open or return HTML path

Requires:
- NetworkX graph built by graph_builder.py
"""

import os
import webbrowser
from typing import Optional

from pyvis.network import Network
import networkx as nx


# ------------------------------------------------------
# Theme-based color palette
# ------------------------------------------------------
THEME_COLORS = {
    "event": "#ff6b6b",        # red-ish
    "cultural": "#4ecdc4",     # teal
    "other": "#ffe66d",        # yellow
    None: "#b2bec3"            # default gray
}


# ------------------------------------------------------
# Convert NetworkX to PyVis
# ------------------------------------------------------
def visualize_graph(
    G: nx.DiGraph,
    output_file: str = "graph_visualization.html",
    height: str = "850px",
    width: str = "100%",
    show: bool = True
) -> str:
    """
    Converts a NetworkX graph into an interactive PyVis HTML file.

    Args:
        G: NetworkX DiGraph
        output_file: where to save the HTML
        show: auto-open browser?
    """

    net = Network(
        height=height,
        width=width,
        directed=True,
        bgcolor="#111111",
        font_color="white"
    )

    # Improve physics behavior
    net.barnes_hut(
        gravity=-3500,
        central_gravity=0.25,
        spring_length=160,
        spring_strength=0.05,
        damping=0.85
    )

    # ------------------------------------------------------
    # Add Nodes
    # ------------------------------------------------------
    for node, attrs in G.nodes(data=True):
        theme = attrs.get("theme")
        tbox = attrs.get("tbox")
        source = attrs.get("source", "")
        color = THEME_COLORS.get(theme, THEME_COLORS[None])

        title_html = f"""
        <b>{node}</b><br>
        Theme: {theme}<br>
        T-Box: {tbox}<br>
        Source: {source}<br>
        """

        net.add_node(
            node,
            label=node,
            title=title_html,
            color=color,
            shape="dot",
            size=25
        )

    # ------------------------------------------------------
    # Add Edges
    # ------------------------------------------------------
    for u, v, attrs in G.edges(data=True):
        predicate = attrs.get("predicate", "")
        span = attrs.get("span", "")
        theme = attrs.get("theme", "")

        title_html = f"""
        <b>{predicate}</b><br>
        Theme: {theme}<br>
        Span: {span}<br>
        """

        net.add_edge(
            u,
            v,
            label=predicate,
            title=title_html,
            arrows="to",
            color="#ffffff"
        )

    # ------------------------------------------------------
    # Render and Save
    # ------------------------------------------------------
    net.set_options("""
    {
        "nodes": {
            "font": { "face": "Arial", "size": 20, "bold": true }
        },
        "edges": {
            "font": { "face": "Arial", "size": 14, "align": "horizontal" },
            "smooth": false
        }
    }
    """)

    

    net.save_graph(output_file)

    if show:
        webbrowser.open("file://" + os.path.realpath(output_file))

    return output_file


# ------------------------------------------------------
# Module Test
# ------------------------------------------------------
if __name__ == "__main__":
    from kg.graph_builder import build_graph_from_triples

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

    G = build_graph_from_triples(triples, theme="event", tbox="dbo:Event", source_file="sample.pdf")
    visualize_graph(G)
