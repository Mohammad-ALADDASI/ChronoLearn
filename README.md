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


---

## Project Timeline (Gantt Chart)

```mermaid
gantt
    title Project Timeline: History Knowledge Graph
    dateFormat  YYYY-MM-DD
    axisFormat  %b %d

    section Phase 1: Research & Theoretical Work
    Understand Assignment               :done, s1, 2025-10-13, 2025-10-19
    Develop Topic & Keywords             :done, s2, 2025-10-20, 2025-10-26
    Search & Read Sources                :done, s3, 2025-10-27, 2025-11-06
    Evaluate Sources & Draft Bibliography :done, s4, 2025-11-07, 2025-11-10
    Revise Search Strategy & Notes       :done, s5, 2025-11-11, 2025-11-17
    Create Research Question / Thesis    :s6, 2025-11-18, 2025-11-21
    Write First Draft                    :active,s7, 2025-11-01, 2025-11-30
    Check for Plagiarism & Citation      :s8, 2025-11-21, 2025-12-16
    Write Second Draft                   :s9, 2025-11-01, 2025-11-30
    Consult Writing Centre               :s10, 2025-12-17, 2025-12-20
    Revise Second Draft                  :s11, 2025-12-21, 2026-01-07
    Proofread & Finalise                 :s12, 2026-01-08, 2026-01-11
    Submit Theoretical Work              :s13, 2026-01-12, 2026-01-15

    section Phase 2: Implementation & Application
    Data Collection & Preprocessing      :s14, 2026-01-15, 2026-02-10
    NLP Entity & Relation Extraction     :s15, 2026-02-11, 2026-03-01
    Knowledge Graph Modeling & Building  :s16, 2026-03-02, 2026-03-25
    Search Interface Development         :s17, 2026-03-26, 2026-04-10
    System Testing & Evaluation          :s18, 2026-04-11, 2026-05-01
    Final Report & Presentation          :s19, 2026-05-02, 2026-05-15

```

---

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
