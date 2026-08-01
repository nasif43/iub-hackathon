import sqlite3
from datetime import datetime
from backend.app.db import get_db_connection
from backend.app.models import ReviewResult, ReviewStatus, ReviewSource, RiskLevel, ClauseCategory

def save_review(
    contract_id: str,
    category: str,
    risk_level: str,
    reason: str,
    contract_evidence: str | None,
    standard_id: str | None,
    standard_text: str | None,
    source: str
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    INSERT INTO reviews (
        contract_id, category, risk_level, reason, contract_evidence,
        standard_id, standard_text, source, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?);
    """, (
        contract_id, category, risk_level, reason, contract_evidence,
        standard_id, standard_text, source, now, now
    ))
    
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return review_id

def get_review_by_id(review_id: int) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM reviews WHERE id = ?;", (review_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def update_review_decision(review_id: int, status: str, reviewer_note: str | None) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
    UPDATE reviews
    SET status = ?, reviewer_note = ?, updated_at = ?
    WHERE id = ?;
    """, (status, reviewer_note, now, review_id))
    
    conn.commit()
    conn.close()
    
    return get_review_by_id(review_id)

def list_reviews_from_db(contract_id: str | None = None, status: str | None = None) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM reviews WHERE 1=1"
    params = []
    
    if contract_id:
        query += " AND contract_id = ?"
        params.append(contract_id)
        
    if status:
        query += " AND status = ?"
        params.append(status)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
