from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional

from backend.app.models import (
    ContractSummary, ContractDetail, Clause, Standard,
    ReviewRequest, ReviewResult, ReviewDecisionRequest, ErrorModel,
    ClauseCategory, RiskLevel, ReviewStatus, ReviewSource,
    ContractCreate, StandardCreate
)
from backend.app.db import get_db_connection
from backend.app.risk_rules import evaluate_risk
from backend.app.explain import build_explanation
from backend.app.review import save_review, get_review_by_id, update_review_decision, list_reviews_from_db
from backend.app.segmenter import segment_contract
from backend.app.classifier import classify_clause, CATEGORIES


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Contract Review Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup exception handler for 404
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": True,
                "code": "NOT_FOUND",
                "message": exc.detail
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": "INTERNAL_ERROR",
            "message": exc.detail
        }
    )

@app.get("/contracts", response_model=List[ContractSummary], tags=["contracts"])
def list_contracts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, parties FROM contracts;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/contracts/{contract_id}", response_model=ContractDetail, tags=["contracts"])
def get_contract(contract_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts WHERE id = ?;", (contract_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} does not exist.")
    return dict(row)

@app.get("/contracts/{contract_id}/clauses", response_model=List[Clause], tags=["contracts"])
def list_contract_clauses(contract_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM contracts WHERE id = ?;", (contract_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} does not exist.")
        
    cursor.execute("SELECT category, heading, text, present FROM clauses WHERE contract_id = ?;", (contract_id,))
    rows = cursor.fetchall()
    conn.close()
    
    clauses = []
    for row in rows:
        clauses.append(Clause(
            category=row["category"],
            present=bool(row["present"]),
            heading=row["heading"],
            text=row["text"]
        ))
    return clauses

@app.get("/standards", response_model=List[Standard], tags=["standards"])
def list_standards():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, text FROM standards;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/contracts", response_model=ContractSummary, tags=["contracts"])
def create_contract(req: ContractCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate next ID
    cursor.execute("SELECT id FROM contracts WHERE id LIKE 'C-USR-%';")
    existing_ids = [row["id"] for row in cursor.fetchall()]
    max_num = 0
    for id_val in existing_ids:
        try:
            num = int(id_val.replace("C-USR-", ""))
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    next_id = f"C-USR-{max_num + 1:03d}"
    
    cursor.execute(
        "INSERT INTO contracts (id, title, parties, raw_text) VALUES (?, ?, ?, ?);",
        (next_id, req.title, req.parties, req.raw_text)
    )
    
    # Segment and insert clauses dynamically
    blocks = segment_contract(req.raw_text)
    found_clauses = {}
    for heading, body in blocks:
        cat = classify_clause(heading, body)
        if cat:
            if cat not in found_clauses:
                found_clauses[cat] = {"headings": [heading], "bodies": [body]}
            else:
                found_clauses[cat]["headings"].append(heading)
                found_clauses[cat]["bodies"].append(body)
                
    # We dynamically load all categories from the dynamic list
    categories = list(CATEGORIES)
    for cat in categories:
        if cat in found_clauses:
            heading_str = " / ".join(found_clauses[cat]["headings"])
            body_str = "\n\n".join(found_clauses[cat]["bodies"])
            cursor.execute(
                "INSERT INTO clauses (contract_id, category, heading, text, present) VALUES (?, ?, ?, ?, 1);",
                (next_id, cat, heading_str, body_str)
            )
        else:
            cursor.execute(
                "INSERT INTO clauses (contract_id, category, heading, text, present) VALUES (?, ?, NULL, NULL, 0);",
                (next_id, cat)
            )
            
    conn.commit()
    conn.close()
    return ContractSummary(id=next_id, title=req.title, parties=req.parties)

@app.post("/standards", response_model=Standard, tags=["standards"])
def create_standard(req: StandardCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO standards (id, category, text) VALUES (?, ?, ?);",
            (req.id, req.category, req.text)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Failed to create standard: {e}")
        
    cursor.execute("SELECT id, category, text FROM standards WHERE id = ?;", (req.id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


@app.post("/review", response_model=ReviewResult, tags=["review"])
def run_review(req: ReviewRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check contract exists
    cursor.execute("SELECT id FROM contracts WHERE id = ?;", (req.contract_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Contract {req.contract_id} does not exist.")
        
    # Get clause
    cursor.execute(
        "SELECT text, present FROM clauses WHERE contract_id = ? AND category = ?;",
        (req.contract_id, req.category.value)
    )
    clause_row = cursor.fetchone()
    
    # Get standard
    cursor.execute(
        "SELECT id, text FROM standards WHERE category = ?;",
        (req.category.value,)
    )
    std_row = cursor.fetchone()
    conn.close()
    
    clause_text = None
    if clause_row and clause_row["present"]:
        clause_text = clause_row["text"]
        
    std_id = None
    std_text = None
    if std_row:
        std_id = std_row["id"]
        std_text = std_row["text"]
        
    # Run deterministic risk comparator
    risk_level, facts, facts_source = evaluate_risk(req.category.value, clause_text)
    
    # Generate explanation
    reason, exp_source = build_explanation(req.category.value, risk_level, facts, clause_text)
    
    # If LLM fact extraction was used, prioritize facts_source over explanation source
    final_source = facts_source if facts_source == "rule_engine+llm_extraction" else exp_source
    
    # If NEI, standard_id and standard_text must be null
    if risk_level == "Not Enough Information":
        std_id = None
        std_text = None
        clause_text = None
        
    review_id = save_review(
        contract_id=req.contract_id,
        category=req.category.value,
        risk_level=risk_level,
        reason=reason,
        contract_evidence=clause_text,
        standard_id=std_id,
        standard_text=std_text,
        source=final_source
    )
    
    # Retrieve saved review
    review_dict = get_review_by_id(review_id)
    if not review_dict:
        raise HTTPException(status_code=500, detail="Failed to save review.")
        
    return ReviewResult(
        review_id=review_dict["id"],
        contract_id=review_dict["contract_id"],
        category=review_dict["category"],
        risk_level=review_dict["risk_level"],
        reason=review_dict["reason"],
        contract_evidence=review_dict["contract_evidence"],
        standard_id=review_dict["standard_id"],
        standard_text=review_dict["standard_text"],
        source=review_dict["source"],
        status=review_dict["status"],
        reviewer_note=review_dict["reviewer_note"],
        human_review="Required"
    )

@app.get("/reviews", response_model=List[ReviewResult], tags=["reviews"])
def list_reviews(contract_id: Optional[str] = None, status: Optional[str] = None):
    reviews = list_reviews_from_db(contract_id, status)
    results = []
    for r in reviews:
        results.append(ReviewResult(
            review_id=r["id"],
            contract_id=r["contract_id"],
            category=r["category"],
            risk_level=r["risk_level"],
            reason=r["reason"],
            contract_evidence=r["contract_evidence"],
            standard_id=r["standard_id"],
            standard_text=r["standard_text"],
            source=r["source"],
            status=r["status"],
            reviewer_note=r["reviewer_note"],
            human_review="Required"
        ))
    return results

@app.post("/reviews/{review_id}/decision", response_model=ReviewResult, tags=["reviews"])
def record_review_decision(review_id: int, req: ReviewDecisionRequest):
    updated = update_review_decision(review_id, req.status.value, req.reviewer_note)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Review ID {review_id} does not exist.")
        
    return ReviewResult(
        review_id=updated["id"],
        contract_id=updated["contract_id"],
        category=updated["category"],
        risk_level=updated["risk_level"],
        reason=updated["reason"],
        contract_evidence=updated["contract_evidence"],
        standard_id=updated["standard_id"],
        standard_text=updated["standard_text"],
        source=updated["source"],
        status=updated["status"],
        reviewer_note=updated["reviewer_note"],
        human_review="Required"
    )
