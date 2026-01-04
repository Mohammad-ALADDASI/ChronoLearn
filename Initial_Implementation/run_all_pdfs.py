"""
run_all_pdfs.py
-------------------
Runs the full semantic pipeline on ALL PDF files inside uploads/.

Pipeline per PDF:
1. Extract text
2. Detect topics
3. Detect theme
4. Generate triples
5. Validate triples

Then:
6. Merge all validated triples into one graph
7. Visualize graph as HTML
8. Export RDF (TTL, JSON-LD, NT)

This script is for batch/offline processing.
"""

import os

from pipeline.pdf_reader import process_pdf
from pipeline.topic_detector import detect_topics
from pipeline.theme_detector import detect_theme
from pipeline.triple_generator import generate_triples
from pipeline.triple_validator import validate_triples
from kg.graph_builder import build_graph_from_triples, merge_graphs
from kg.graph_visualiser import visualize_graph
from pipeline.rdf_exporter import export_rdf


UPLOAD_DIR = "uploads"


def run_pipeline_for_all_pdfs():
    all_graphs = []
    summary = []

    print("\n🔍 Looking for PDF files in /uploads...")

    for filename in os.listdir(UPLOAD_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(UPLOAD_DIR, filename)
        print(f"\n📄 Processing: {filename}")

        # 1. Extract text
        text = process_pdf(pdf_path)
        print("   ✔ Extracted text")

        # 2. Detect topics
        topic_result = detect_topics(text)
        topics = topic_result["topics"][:2]  # pick first 2 automatically
        print(f"   ✔ Topics: {topics}")

        # 3. Detect theme
        theme_result = detect_theme(text)
        theme = theme_result["theme"]
        print(f"   ✔ Theme: {theme}")

        # 4. Generate triples
        triple_result = generate_triples(text, topics, theme)
        triples = triple_result["triples"]
        print(f"   ✔ Generated triples: {len(triples)}")

        # 5. Validate triples
        validated = validate_triples(triples, text)
        valid_triples = validated["valid"] + validated["repaired"]
        print(f"   ✔ Valid triples: {len(valid_triples)}")

        # 6. Build graph for this PDF
        G = build_graph_from_triples(
            valid_triples,
            theme,
            triple_result["tbox"],
            source_file=filename
        )

        all_graphs.append(G)

        summary.append({
            "file": filename,
            "theme": theme,
            "topics": topics,
            "triples": len(valid_triples)
        })

    # 7. Merge into one global graph
    print("\n🔄 Merging all graphs...")
    full_graph = merge_graphs(all_graphs)

    # 8. Visualize
    print("🌐 Generating graph visualization...")
    visualize_graph(full_graph)

    # 9. Export RDF
    print("📦 Exporting RDF...")
    paths = export_rdf(
        triples=[
            t  # flatten triple lists
            for G in all_graphs
            for u, v, attrs in G.edges(data=True)
            for t in [{"subject": u, "predicate": attrs["predicate"], "object": v, "span": attrs["span"]}]
        ],
        tbox="dbo:Entity"  # generic for multi-file scenarios
    )

    print("📄 RDF exported:")
    for fmt, path in paths.items():
        print(f"  → {fmt}: {path}")

    print("\n📊 Summary:")
    for item in summary:
        print(f"  {item['file']}: {item['triples']} triples, theme={item['theme']}, topics={item['topics']}")

    print("\n🎉 Finished! All PDFs processed.\n")


if __name__ == "__main__":
    run_pipeline_for_all_pdfs()
