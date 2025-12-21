# ENR — Semantic Knowledge Graph Extraction System

## UI Mockup (Human-in-the-Loop, Ontology-First)

This mockup describes a **web-based UI** (Flask backend, future React/Streamlit front-end) that exposes semantic control points while keeping the pipeline explainable and ontology-governed.

---

## 1. Global Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ENR Semantic Knowledge Graph Extraction System               │
│ Ontology-first • Arabic-aware • Human-in-the-loop            │
├───────────────┬─────────────────────────────────────────────┤
│ Left Sidebar  │ Main Workspace                               │
│               │                                             │
│ • Uploads     │  Contextual panel (changes per step)        │
│ • Ontologies  │                                             │
│ • Pipeline    │                                             │
│ • Graph View  │                                             │
│ • RDF Export  │                                             │
│ • Logs        │                                             │
└───────────────┴─────────────────────────────────────────────┘
```

**Design tone:** academic, neutral, low-noise (no dashboards, no gamification)

---

## 2. Step 1 — Document Ingestion

### Screen: Upload & Preview

```
┌──────────────── Upload Documents ────────────────┐
│ [ Select PDF(s) ]   uploads/                     │
│                                                  │
│ Uploaded Files:                                  │
│  ▸ 1948_Memoirs.pdf                              │
│  ▸ Oral_History_Jerusalem.pdf                    │
│                                                  │
│ [ Extract Text ]                                 │
└──────────────────────────────────────────────────┘

┌────────────── Extracted Text Preview ─────────────┐
│ Arabic text (normalized):                          │
│                                                    │
│ "في عام 1948، وقعت أحداث..."                      │
│                                                    │
│ Diacritics removed • Unicode normalized            │
└───────────────────────────────────────────────────┘
```

**User control:** verify extraction quality before semantics begin

---

## 3. Step 2 — Topic Detection (Human-in-the-Loop)

### Screen: Topic Suggestions

```
┌──────────── Detected Topics (LLM) ───────────────┐
│ Please select 1–3 core topics to guide extraction │
│                                                   │
│ ☐ 1948 Arab–Israeli War                            │
│ ☐ Palestinian displacement                        │
│ ☐ Jerusalem neighborhoods                         │
│ ☐ British Mandate governance                      │
│                                                   │
│ [ Confirm Topics ]                                │
└───────────────────────────────────────────────────┘
```

**Constraint:** pipeline does not proceed without explicit topic confirmation

---

## 4. Step 3 — Theme Classification

### Screen: Semantic Mode Selection

```
┌──────────── Content Classification ──────────────┐
│ Detected dominant theme:                          │
│                                                   │
│  ● Event-based (historical, temporal)             │
│  ○ Cultural (customs, identities, heritage)       │
│  ○ Custom (user-defined ontology)                 │
│                                                   │
│ Active T-Box:                                     │
│  ▸ event.tbox.ttl                                 │
│                                                   │
│ [ Load Ontology & Continue ]                      │
└───────────────────────────────────────────────────┘
```

Ontology selection **locks predicate space** for all next steps

---

## 5. Step 4 — Ontology Inspector (T-Box Transparency)

### Screen: Ontology Viewer (Read-only)

```
┌──────────── Ontology Constraints ────────────────┐
│ Classes:                                         │
│  • Event                                         │
│  • Agent                                         │
│  • Place                                         │
│                                                  │
│ Predicates:                                      │
│  • hasAgent     (Event → Agent)                  │
│  • occurredAt   (Event → Place)                  │
│  • hasDate      (Event → xsd:date)               │
│                                                  │
│ ❗ Only these predicates may be generated         │
└───────────────────────────────────────────────────┘
```

**Purpose:** prevent hallucinated or linguistic predicates

---

## 6. Step 5 — Event Segmentation & Triple Generation

### Screen: Event Blocks with Grounding

```
┌──────────── Event Block: Event_1 ────────────────┐
│ Text Span:                                       │
│ "في نيسان 1948، تم تهجير سكان حي..."             │
│                                                   │
│ Generated Triples:                               │
│  • Event_1 hasAgent Palestinian_Civilians        │
│  • Event_1 occurredAt Jerusalem                  │
│  • Event_1 hasDate 1948-04                       │
│                                                   │
│ [ Accept ]   [ Edit ]   [ Reject ]               │
└───────────────────────────────────────────────────┘
```

**Key rule:** no triple exists without a visible grounding span

---

## 7. Step 6 — Validation & Repair

### Screen: Validation Report

```
┌──────────── Triple Validation ───────────────────┐
│ ✔ Predicate allowed by ontology                  │
│ ✔ Domain / Range valid                           │
│ ✔ Grounding span exists                          │
│ ⚠ Duplicate entity detected: Jerusalem           │
│                                                   │
│ Suggested Repair:                                │
│  → Merge with existing Place: Jerusalem           │
│                                                   │
│ [ Apply Repair ]  [ Ignore ]                     │
└───────────────────────────────────────────────────┘
```

LLM repair is **optional and controlled**

---

## 8. Step 7 — Knowledge Graph Visualization

### Screen: Interactive Graph

```
┌──────────── Knowledge Graph ─────────────────────┐
│  (PyVis interactive canvas)                       │
│                                                   │
│  ● Event_1 ──hasAgent──▶ Palestinian_Civilians    │
│     │                                            │
│     └─occurredAt──▶ Jerusalem                    │
│                                                   │
│ Legend:                                          │
│  ● Event   ■ Agent   ▲ Place                     │
└───────────────────────────────────────────────────┘
```

Graph is **ontology-driven**, not force-directed text blobs

---

## 9. Step 8 — RDF Export

### Screen: Export Panel

```
┌──────────── RDF Export ──────────────────────────┐
│ Select format:                                   │
│  ☐ Turtle (.ttl)                                 │
│  ☐ JSON-LD                                       │
│  ☐ N-Triples                                     │
│                                                   │
│ Features:                                        │
│  ✔ Canonical URIs                                │
│  ✔ dbo:Event typing                              │
│  ✔ No duplicate entities                         │
│                                                   │
│ [ Export Knowledge Graph ]                       │
└───────────────────────────────────────────────────┘
```

---

## 10. Logs & Explainability Panel (Optional)

```
┌──────────── Pipeline Log ────────────────────────┐
│ [INFO] Loaded event.tbox.ttl                     │
│ [INFO] 3 topics confirmed by user                │
│ [WARN] Predicate rejected: "influencedBy"       │
│ [INFO] RDF export successful                     │
└───────────────────────────────────────────────────┘
```

---

## Design Summary

• Ontology is visible, not hidden
• User intervenes **before meaning is fixed**
• Every triple is explainable
• UI supports scholarship, not automation theater

---
