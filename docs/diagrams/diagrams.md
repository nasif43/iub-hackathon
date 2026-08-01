# Architecture & Workflow Diagrams

This document contains Mermaid diagrams illustrating the Contract Review Assistant (CRA) architecture, the core data flow, and how the deterministic safety engine ensures safe assessments.

## 1. System Architecture

```mermaid
graph TD
    User([User / Reviewer]) -->|Interacts| StreamlitApp[Streamlit Frontend UI]
    StreamlitApp -->|HTTP REST Requests| FastAPI[FastAPI Backend Server]
    
    subgraph FastAPI Backend App
        FastAPI --> Main[main.py Router]
        Main --> db[db.py Database Wrapper]
        Main --> loader[loader.py Startup Seeder]
        Main --> segmenter[segmenter.py Clause Segmenter]
        Main --> classifier[classifier.py Clause Classifier]
        Main --> risk[risk_rules.py Risk Evaluator]
        Main --> explain[explain.py Explanation Builder]
    end
    
    loader -->|Reads Raw Data| RawData[(Raw JSON & TXT Dataset)]
    db -->|Reads / Writes| SQLite[(SQLite Database: cra.db)]
```

## 2. Review Request Pipeline (Data Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as Human Reviewer
    participant UI as Streamlit Frontend
    participant API as FastAPI Backend
    participant DB as SQLite (cra.db)
    participant Rules as Rule Engine (risk_rules.py)

    User->>UI: Select Contract & Click "Run Review"
    UI->>API: POST /review { contract_id, category }
    API->>DB: Query selected clause & standard
    DB-->>API: Return clause text & standard text
    alt Clause is missing
        API-->>UI: Return "Not Enough Information" (Safety Abstention)
    else Clause is present
        API->>Rules: Evaluate risk & extract facts
        Rules-->>API: Return Risk Level & Extracted Facts
        API->>API: Build template explanation
        API->>DB: Persist pending review row
        API-->>UI: Return ReviewResult (Evidence, Standard, Risk Level, Explanation)
    end
    UI->>User: Render Result Card & Decision Actions (Approve/Reject)
```

## 3. Safety Abstention Logic (Anti-Hallucination Guard)

```mermaid
graph TD
    Start([Review Triggered]) --> CheckClause{Clause Present in Contract?}
    CheckClause -->|No| Abstain[Return 'Not Enough Information' & Explain absence]
    CheckClause -->|Yes| ExtractFacts[Extract facts: numbers, dates, structures]
    
    ExtractFacts --> CheckFacts{All required numbers parsed?}
    CheckFacts -->|No| RiskScored[Score absence as risk contributor within Low/Med/High]
    CheckFacts -->|Yes| Compare[Deterministic comparison against standards]
    
    Compare --> RiskResult[Assign Low / Medium / High Risk]
    RiskScored --> RiskResult
    
    RiskResult --> Output([Show verbatim evidence + risk result])
```
