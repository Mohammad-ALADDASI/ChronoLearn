"""
new_app.py
-------------------
Full Flask backend for the Semantic Triple Extraction Pipeline.

Endpoints:
  /extract_text          → PDF → text
  /detect_topics         → topics + keywords
  /detect_theme          → event/cultural/other
  /generate_triples      → LLM triples (chunk-based)
  /validate_triples      → Pydantic + grounding checks
  /lookup_predicates     → DBpedia/Wikidata relations
  /visualize_graph       → PyVis HTML graph
  /export_rdf            → TTL, JSON-LD, N-Triples

This replaces the old NER-only approach with a semantic triple-based KG pipeline.
"""

import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Stage 1: PDF + text
from pipeline.pdf_reader import process_pdf

# Stage 2: Topic detection
from pipeline.topic_detector import detect_topics

# Stage 3: Theme detection
from pipeline.theme_detector import detect_theme

# Stage 4: Triple generation
from pipeline.triple_generator import generate_triples

# Stage 5: Triple validation
from pipeline.triple_validator import validate_triples

# Stage 6: Relation lookup
from pipeline.relation_lookup import get_semantic_alternatives

# Stage 7: Graph building + visualization
from kg.graph_builder import build_graph_from_triples
from kg.graph_visualiser import visualize_graph

# Stage 8: RDF exporter
from pipeline.rdf_exporter import export_rdf


# ------------------------------------------------------
# Flask Setup
# ------------------------------------------------------
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("triples", exist_ok=True)


# ------------------------------------------------------
# Endpoint 1 — Extract text from PDF
# ------------------------------------------------------
@app.route("/extract_text", methods=["POST"])
def api_extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(pdf_path)

    try:
        text = process_pdf(pdf_path)
        return jsonify({"filename": filename, "text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------
# Endpoint 2 — Topic Detection
# ------------------------------------------------------
@app.route("/detect_topics", methods=["POST"])
def api_detect_topics():
    data = request.json
    text = data.get("text", "")

    result = detect_topics(text)
    return jsonify(result)


# ------------------------------------------------------
# Endpoint 3 — Theme Detection
# ------------------------------------------------------
@app.route("/detect_theme", methods=["POST"])
def api_detect_theme():
    data = request.json
    text = data.get("text", "")

    result = detect_theme(text)
    return jsonify(result)


# ------------------------------------------------------
# Endpoint 4 — Triple Generation
# ------------------------------------------------------
@app.route("/generate_triples", methods=["POST"])
def api_generate_triples():
    data = request.json

    text = data.get("text", "")
    topics = data.get("topics", [])
    theme = data.get("theme", "")
    user_tbox = data.get("tbox")

    result = generate_triples(text, topics, theme, user_tbox)
    return jsonify(result)


# ------------------------------------------------------
# Endpoint 5 — Triple Validation
# ------------------------------------------------------
@app.route("/validate_triples", methods=["POST"])
def api_validate_triples():
    data = request.json

    triples = data.get("triples", [])
    text = data.get("text", "")

    result = validate_triples(triples, text, auto_repair=True)
    return jsonify(result)


# ------------------------------------------------------
# Endpoint 6 — Predicate Lookup
# ------------------------------------------------------
@app.route("/lookup_predicates", methods=["POST"])
def api_lookup_predicates():
    data = request.json
    predicate = data.get("predicate", "")

    result = get_semantic_alternatives(predicate)
    return jsonify(result)


# ------------------------------------------------------
# Endpoint 7 — Graph Visualization
# ------------------------------------------------------
@app.route("/visualize_graph", methods=["POST"])
def api_visualize_graph():
    data = request.json

    triples = data.get("triples", [])
    theme = data.get("theme", "")
    tbox = data.get("tbox", "")
    source = data.get("source", "")

    G = build_graph_from_triples(triples, theme, tbox, source_file=source)
    html_path = visualize_graph(G)

    return jsonify({"html_path": html_path})


# ------------------------------------------------------
# Endpoint 8 — RDF Export
# ------------------------------------------------------
@app.route("/export_rdf", methods=["POST"])
def api_export_rdf():
    data = request.json

    triples = data.get("triples", [])
    tbox_class = data.get("tbox", "dbo:Entity")
    formats = data.get("formats", ["ttl", "jsonld", "nt"])
    theme = data.get("theme", "event")

    paths = export_rdf(triples, tbox_class, theme, formats=formats)
    return jsonify(paths)


# ------------------------------------------------------
# Hello Test (optional)
# ------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {"message": "Semantic Triple Extraction API is running."}
    )


# ------------------------------------------------------
# Launch App
# ------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Semantic Flask API running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
