import os
import json
import codecs
import unicodedata
import networkx as nx
from pyvis.network import Network
import webbrowser

ENTITIES_FOLDER = "entities"

# ------------------------------------------------------
# Fix Arabic without harming English
# ------------------------------------------------------
def normalize_arabic(s):
    if not isinstance(s, str):
        return s

    original = s

    # Keywords that must NEVER be modified
    json_keys = ["source", "target", "type", "Relations"]
    if s in json_keys:
        return s

    # Detect if Arabic exists
    contains_arabic = any("\u0600" <= c <= "\u06FF" for c in s)

    # If no Arabic → keep English intact
    if not contains_arabic:
        return s

    # Fix corrupted UTF-8: Ã˜Ã— style
    if any(bad in s for bad in ["Ã", "Â", "¢", "¦", "¤", "â"]):
        try:
            fixed = s.encode("latin1").decode("utf-8")
            if any("\u0600" <= c <= "\u06FF" for c in fixed):
                return fixed
        except:
            pass

    # Decode \u0627\u0644 escape sequences
    if "\\u" in s:
        try:
            fixed = codecs.decode(s, "unicode_escape")
            return fixed
        except:
            pass

    # Normalize normal Arabic
    return unicodedata.normalize("NFC", s)


# ------------------------------------------------------
# Safely parse ANY form of JSON stored in "entities"
# ------------------------------------------------------
def parse_entities(entities_raw, filename):
    if isinstance(entities_raw, dict):
        return entities_raw  # already correct

    if not isinstance(entities_raw, str):
        print(f"⚠️ Unexpected entity type in {filename}")
        return {}

    text = entities_raw.strip()

    # Remove Markdown fences if present
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    # Try loading normally
    try:
        return json.loads(text)
    except:
        pass

    # Maybe escape sequences need decoding
    try:
        text2 = codecs.decode(text, "unicode_escape")
        return json.loads(text2)
    except:
        pass

    print(f"❌ Could NOT parse entities inside {filename}")
    return {}


# ------------------------------------------------------
# Load & fix entity files
# ------------------------------------------------------
def load_all_entities(folder):
    merged = {
        "أشخاص": set(),
        "أماكن": set(),
        "منظمات": set(),
        "تواريخ": set(),
        "أحداث": set(),
        "Relations": []
    }

    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(folder, filename)
        print(f"📄 Loading: {filename}")

        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        entities_raw = raw.get("entities")

        # Parse dictionary no matter how it's stored
        entities = parse_entities(entities_raw, filename)

        if not isinstance(entities, dict):
            print(f"⚠️ Skipping {filename} (bad structure)")
            continue

        for key, value in entities.items():
            if key == "Relations":
                continue

            if isinstance(value, list):
                for item in value:
                    merged.setdefault(key, set()).add(normalize_arabic(item))

        # Add relations if exist
        if "Relations" in entities:
            merged["Relations"].extend(entities["Relations"])

    # Convert sets → lists
    return {k: (list(v) if isinstance(v, set) else v) for k, v in merged.items()}


# ------------------------------------------------------
# Add graph edges automatically
# ------------------------------------------------------
def auto_generate_relationships(entities):
    relations = []
    pairs = [
        ("أشخاص", "أماكن", "مرتبط بـ المكان"),
        ("أشخاص", "منظمات", "مرتبط بـ المنظمة"),
        ("أماكن", "أحداث", "حدث في"),
        ("أشخاص", "أحداث", "متعلق بـ الحدث"),
        ("منظمات", "أحداث", "شارك في"),
    ]

    for src, tgt, label in pairs:
        for s in entities.get(src, []):
            for t in entities.get(tgt, []):
                relations.append({"source": s, "target": t, "type": label})

    return relations


# ------------------------------------------------------
# Build graph
# ------------------------------------------------------
def build_graph(entities):
    G = nx.DiGraph()

    # Add nodes
    for category, items in entities.items():
        if category == "Relations":
            continue

        for item in items:
            G.add_node(
                item,
                label=item,
                title=category,
                group=category,
                shape="dot",
                font={"face": "Arial", "size": 22},
		physics=False
            )

    # Add relations
    relations = entities["Relations"]
    relations.extend(auto_generate_relationships(entities))

    for rel in relations:
        s, t = rel.get("source"), rel.get("target")
        label = rel.get("type", "علاقة")

        if s and t:
            G.add_edge(s, t, title=label, label=label)

    return G


# ------------------------------------------------------
# Visualize Graph
# ------------------------------------------------------
def visualize_graph(G):
    net = Network(
        height="850px",
        width="100%",
        directed=True,
        bgcolor="#111111",
        font_color="white"
    )

    net.barnes_hut(
        gravity=-3000,
        central_gravity=0.2,
        spring_length=140,
        spring_strength=0.05
    )

    net.from_nx(G)

    output_file = "all_entities_graph.html"
    net.write_html(output_file)

    # Inject font fixes
    with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    html = html.replace(
        "nodes: {",
        """nodes: {
            font: { face: "Arial", size: 22, bold: true },
        """
    )

    html = html.replace(
        "edges: {",
        """edges: {
            font: { face: "Arial", size: 16 },
        """
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n🎉 Graph generated → {output_file}\n")
    webbrowser.open("file://" + os.path.realpath(output_file))
