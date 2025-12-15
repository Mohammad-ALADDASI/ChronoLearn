"""
relation_lookup.py
---------------------
Provides semantic lookup for predicates using DBpedia and Wikidata SPARQL APIs.

Functions:
- get_dbpedia_relations(keyword)
- get_wikidata_properties(keyword)
- get_semantic_alternatives(predicate)
- caching for performance

This module is used after triple validation to help the user refine predicates.
"""

import requests
from functools import lru_cache
from typing import List, Dict, Any
import urllib.parse


# ------------------------------------------------------
# SPARQL Endpoints
# ------------------------------------------------------
DBPEDIA_SPARQL = "https://dbpedia.org/sparql"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"


# ------------------------------------------------------
# Utility: run SPARQL query
# ------------------------------------------------------
def run_sparql(endpoint: str, query: str) -> Dict[str, Any]:
    headers = {
        "Accept": "application/sparql-results+json"
    }

    response = requests.get(endpoint, params={"query": query}, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"SPARQL query failed ({response.status_code}): {response.text}"
        )

    return response.json()


# ------------------------------------------------------
# DBpedia Predicate Lookup
# ------------------------------------------------------
@lru_cache(maxsize=128)
def get_dbpedia_relations(keyword: str) -> List[Dict[str, str]]:
    """
    Searches DBpedia for any property whose English or Arabic label
    matches the keyword.
    """

    keyword = keyword.strip()
    safe_kw = urllib.parse.quote(keyword)

    query = f"""
    SELECT ?property ?label WHERE {{
        ?property a rdf:Property ;
                  rdfs:label ?label .
        FILTER (LANG(?label) IN ('en', 'ar'))
        FILTER (REGEX(?label, "{safe_kw}", "i"))
    }}
    LIMIT 50
    """

    data = run_sparql(DBPEDIA_SPARQL, query)

    results = []
    for item in data["results"]["bindings"]:
        results.append({
            "property": item["property"]["value"],
            "label": item["label"]["value"]
        })

    return results


# ------------------------------------------------------
# Wikidata Predicate Lookup
# ------------------------------------------------------
@lru_cache(maxsize=128)
def get_wikidata_properties(keyword: str) -> List[Dict[str, str]]:
    """
    Searches Wikidata for matching properties.
    """

    keyword = keyword.strip()

    query = f"""
    SELECT ?property ?propertyLabel WHERE {{
      ?property a wikibase:Property ;
                rdfs:label ?propertyLabel .
      FILTER(LANG(?propertyLabel)='en')
      FILTER(CONTAINS(LCASE(?propertyLabel), "{keyword.lower()}"))
    }}
    LIMIT 50
    """

    data = run_sparql(WIKIDATA_SPARQL, query)

    results = []
    for item in data["results"]["bindings"]:
        results.append({
            "property": item["property"]["value"],
            "label": item["propertyLabel"]["value"]
        })

    return results


# ------------------------------------------------------
# Semantic Alternatives Suggestion
# ------------------------------------------------------
def get_semantic_alternatives(predicate: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Given a predicate string (Arabic or English), return:
    {
        "dbpedia": [...],
        "wikidata": [...]
    }

    This is used by the UI to help users refine relationships.
    """

    if not predicate or len(predicate.strip()) < 2:
        return {"dbpedia": [], "wikidata": []}

    predicate = predicate.strip()

    dbpedia_results = get_dbpedia_relations(predicate)
    wikidata_results = get_wikidata_properties(predicate)

    return {
        "dbpedia": dbpedia_results,
        "wikidata": wikidata_results
    }


# ------------------------------------------------------
# Module Test
# ------------------------------------------------------
if __name__ == "__main__":
    predicate = "located"
    print("Testing DBpedia + Wikidata search for:", predicate)
    result = get_semantic_alternatives(predicate)
    print(result)
