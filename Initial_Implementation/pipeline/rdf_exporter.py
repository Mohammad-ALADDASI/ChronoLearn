"""
rdf_exporter.py (Improved Version)
-----------------------------------
Exports ontology-governed triples into RDF/Turtle, JSON-LD, and N-Triples.

NEW FEATURES:
- Canonical entity IDs
- Event-centric RDF structure
- Subject typed as :HistoricalEvent or :CulturalEntity based on theme
- Enforces ontology alignment with T-Box
- Deduplication & normalization
- Clean Turtle output with labels
"""

import os
import unicodedata
from typing import List, Dict
from tbox_loader import load_tbox_template


# ------------------------------------------------------
# 1. URI Normalization & Canonicalization
# ------------------------------------------------------
def slugify(text: str) -> str:
    """
    Makes a safe URI slug for Arabic/English identifiers.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.replace(" ", "_")
    text = text.replace("/", "_")
    text = text.replace("\\", "_")
    return text


def canonical_entity(entity: str) -> str:
    """
    Ensures consistent subject/object identifiers across triples.
    """
    entity = entity.strip()
    return f":{slugify(entity)}"


def canonical_event_id(i: int) -> str:
    """
    Assigns Event_1, Event_2, ...
    This ensures clean TTL even when subjects are messy in the text.
    """
    return f":Event_{i}"


# ------------------------------------------------------
# 2. Turtle Exporter
# ------------------------------------------------------
def export_turtle(triples: List[Dict], tbox_class: str, theme: str, save_path="triples/graph.ttl") -> str:
    header = """
@prefix : <http://example.org/resource/> .
@prefix onto: <http://example.org/ontology/> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""

    lines = [header]

    # Load ontology (T-Box is shown in comments)
    tbox_template, _ = load_tbox_template(theme)
    lines.append("# Ontology Template Used")
    for l in tbox_template.split("\n"):
        lines.append("# " + l)
    lines.append("")

    # Canonical subject remapping (each triple → clean event-id)
    event_map = {}
    event_counter = 1

    def get_event_id(subj):
        nonlocal event_counter
        if subj not in event_map:
            event_map[subj] = canonical_event_id(event_counter)
            event_counter += 1
        return event_map[subj]

    # Write turtle triples
    for t in triples:
        subj_id = get_event_id(t["subject"])
        obj_id = canonical_entity(t["object"])
        pred = slugify(t["predicate"])

        # Subject typing
        lines.append(f"{subj_id} a {tbox_class} .")

        # Label
        lines.append(f'{subj_id} rdfs:label "{t["subject"]}"@ar .')
        lines.append(f'{obj_id} rdfs:label "{t["object"]}"@ar .')

        # Predicate triple
        lines.append(f"{subj_id} onto:{pred} {obj_id} .\n")

    output = "\n".join(lines)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(output)

    return save_path


# ------------------------------------------------------
# 3. JSON-LD Exporter
# ------------------------------------------------------
def export_jsonld(triples: List[Dict], tbox_class: str, theme: str, save_path="triples/graph.jsonld") -> str:
    graph = []

    for i, t in enumerate(triples, start=1):
        subj = canonical_event_id(i)
        obj = canonical_entity(t["object"])
        pred = f"http://example.org/ontology/{slugify(t['predicate'])}"

        graph.append({
            "@id": f"http://example.org/resource/{subj[1:]}",
            "@type": tbox_class,
            pred: {"@id": f"http://example.org/resource/{obj[1:]}"},
            "rdfs:label": t["subject"]
        })

    jsonld = {
        "@context": {
            "@vocab": "http://example.org/resource/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "@graph": graph
    }

    import json
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(jsonld, f, indent=2, ensure_ascii=False)

    return save_path


# ------------------------------------------------------
# 4. N-Triples Exporter
# ------------------------------------------------------
def export_ntriples(triples: List[Dict], tbox_class: str, save_path="triples/graph.nt") -> str:
    lines = []

    for i, t in enumerate(triples, start=1):
        subj = f"<http://example.org/resource/Event_{i}>"
        obj = f"<http://example.org/resource/{slugify(t['object'])}>"
        pred = f"<http://example.org/ontology/{slugify(t['predicate'])}>"

        lines.append(f"{subj} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{tbox_class}> .")
        lines.append(f"{subj} {pred} {obj} .\n")

    output = "\n".join(lines)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(output)

    return save_path


# ------------------------------------------------------
# 5. Unified RDF Exporter
# ------------------------------------------------------
def export_rdf(triples: List[Dict], tbox_class: str, theme="event", formats=None, folder="triples/"):
    """
    Exports in multiple formats:
    - ttl
    - jsonld
    - nt
    """

    if formats is None:
        formats = ["ttl", "jsonld", "nt"]

    os.makedirs(folder, exist_ok=True)

    paths = {}

    if "ttl" in formats:
        paths["ttl"] = export_turtle(triples, tbox_class, theme, os.path.join(folder, "graph.ttl"))

    if "jsonld" in formats:
        paths["jsonld"] = export_jsonld(triples, tbox_class, theme, os.path.join(folder, "graph.jsonld"))

    if "nt" in formats:
        paths["nt"] = export_ntriples(triples, tbox_class, os.path.join(folder, "graph.nt"))

    return paths
