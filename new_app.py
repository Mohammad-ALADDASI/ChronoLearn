"""
This will be the NEW Flask application using the semantic triple pipeline.

We keep your existing app.py intact,
and migrate endpoints into this new structure gradually.
"""
from flask import Flask

app = Flask(__name__)

# TODO: implement new endpoints:
# /extract_text
# /detect_topics
# /detect_theme
# /generate_triples
# /validate_triples
# /lookup_predicates
# /visualize_graph
# /export_rdf

if __name__ == "__main__":
    app.run(debug=True, port=5001)
