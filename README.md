# ChronoLang
### Graduation Project — Data Science & Artificial Intelligence

**Authors:** Mohammad ALADDASI & Shahd Abuhijleh

**Supervisor:** *Dr Omar Qawasmeh*
 
**Institution:** *Princess Summaya University for Technology*

**Academic Year:** 2025–2026

---

## Project Overview

This project aims to develop a **history-based Knowledge Graph (KG)** that can power a **frontend** capable of reasoning, linking, and contextualising historical information. The system will extract structured knowledge from diverse sources (texts, timelines, archives) to create a semantic network of **events, people, places, and time periods**.

The project bridges **data science**, **NLP**, **LLM**, and **knowledge representation** — providing an intelligent exploration tool for historical research, education, and cultural preservation.

---

## Research Question

> **How can a history-based Knowledge Graph provide an interactive and intelligent way to represent historical data compared to traditional text-based representations?**

---

## Objectives

* Build a **Knowledge Graph** representing entities and their relationships.
* Design an **ETL/ELT pipeline** for ingesting structured and unstructured  data.
* Integrate **natural language processing (NLP)** for entity extraction and relation identification.
* Implement a **smart query system** for semantic exploration and reasoning.
* Evaluate system performance through query relevance and reasoning accuracy.

---

## Methodology

1. **Data Collection** – Scrape and preprocess texts from open-access archives and APIs.
2. **Entity & Relation Extraction** – Use NLP pipelines for named entity recognition (NER) and dependency parsing.
3. **Knowledge Graph Construction** – Build and populate using RDF/OWL or Neo4j.
4. **Query Interface** – Develop a front-end or command-line interface for semantic search.
5. **Evaluation** – Compare with keyword-based search performance on historical questions.

---

## Technologies

| **Component**       | **Tools / Technologies**                                     |
|---------------------|--------------------------------------------------------------|
| **Programming**     | Python - Jupyter Notebook                                    |
| **NLP**             | Omartificial                                                 |
| **Knowledge Graph** | Neo4j, RDFLib                                                |
| **Vector Store**    | ChromaDB                                                     |
| **Data Pipeline**   | Pandas, BeautifulSoup, Scrapy, Selenium                      |
| **LLM Models**      | Aya Model, Qwen, OSS2b *(if feasible)*                       |
| **Evaluation**      | Precision / Recall, SPARQL Queries, Cypher                   |
| **Visualization**   | Cytoscape.js, Vis Network (Vis.js), Sigma.js, D3.js         |

## Project Timeline (Gantt Chart)

```mermaid
gantt
    title Project Timeline: History Knowledge Graph (Revised)
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    %% -------------------------
    %% PHASE 1 — GP1 DOCUMENTATION
    %% -------------------------
    section GP1 Documentation (Research + Writing)
    Understand Assignment                     :done, gp1a, 2025-10-13, 2025-10-19
    Develop Topic & Keywords                  :done, gp1b, 2025-10-20, 2025-10-26
    Search & Read Sources                     :done, gp1c, 2025-10-27, 2025-11-06
    Evaluate Sources & Draft Bibliography     :done, gp1d, 2025-11-07, 2025-11-10
    Revise Search Strategy & Notes            :done, gp1e, 2025-11-11, 2025-11-17
    Create Research Question / Thesis         :active, gp1f, 2025-11-18, 2025-11-21

    %% Writing overlaps heavily with development tasks (correct GP1 behaviour)
    First Draft (Theory Chapters)             :active, gp1g, 2025-11-01, 2025-12-30
    Second Draft (Methodology + Design)       :gp1h, 2025-12-15, 2026-01-20
    Proofread & Finalise GP1 Report           :gp1i, 2026-01-21, 2026-01-30
    Submit GP1 Deliverables                   :milestone, gp1m, 2026-01-31, 0d

    %% -------------------------
    %% PHASE 2 — GP2 PRACTICAL WORK (starts before GP1 ends)
    %% -------------------------
    section GP2 Practical System Development

    %% Starts during GP1 (concurrent)
    Data Collection & Preprocessing           :active, gp2a, 2025-12-20, 2026-02-10
    NLP Entity & Relation Extraction          :gp2b, 2026-01-15, 2026-03-01

    %% KG modelling overlaps documentation of methodology (concurrency added)
    Knowledge Graph Modeling & Building       :gp2c, 2026-02-10, 2026-03-25

    Search Interface Development              :gp2d, 2026-03-05, 2026-04-10
    System Testing & Evaluation               :gp2e, 2026-04-05, 2026-05-01

    %% Documentation continues during all these tasks (true GP1/GP2 flow)
    Final Documentation + Presentation Prep   :gp2f, 2026-04-20, 2026-05-15
    Submit Final Deliverables (GP2)           :milestone, gp2m, 2026-05-15, 0d

## Deliverables

* Research Paper (APA7 Format)
* Functional Prototype of the Knowledge Graph Search Engine
* Evaluation Report
* Presentation Slides

---

## Citation & Resources
* If you use this project or its ideas, please cite appropriately.
This repository follows the [APA 7th Edition](https://apastyle.apa.org/) citation format.
---

## Acknowledgments

Special thanks to the **Data Science & AI Department** especially **Dr Omar Qawasmeh** for guidance and resources.
