import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "./data/cra.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Drop existing tables to ensure clean, idempotent start
    cursor.execute("DROP TABLE IF EXISTS rules;")
    cursor.execute("DROP TABLE IF EXISTS questions;")
    cursor.execute("DROP TABLE IF EXISTS reviews;")
    cursor.execute("DROP TABLE IF EXISTS clauses;")
    cursor.execute("DROP TABLE IF EXISTS standards;")
    cursor.execute("DROP TABLE IF EXISTS contracts;")
    
    # Create contracts table
    cursor.execute("""
    CREATE TABLE contracts (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        parties TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        dataset_note TEXT
    );
    """)
    
    # Create standards table
    cursor.execute("""
    CREATE TABLE standards (
        id TEXT PRIMARY KEY,
        category TEXT UNIQUE NOT NULL,
        text TEXT NOT NULL
    );
    """)
    
    # Create clauses table
    cursor.execute("""
    CREATE TABLE clauses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id TEXT NOT NULL,
        category TEXT NOT NULL,
        heading TEXT,
        text TEXT,
        present INTEGER NOT NULL CHECK (present IN (0, 1)),
        FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clauses_contract_category ON clauses (contract_id, category);")
    
    # Create reviews table
    cursor.execute("""
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id TEXT NOT NULL,
        category TEXT NOT NULL,
        risk_level TEXT NOT NULL CHECK (risk_level IN ('Low Risk', 'Medium Risk', 'High Risk', 'Not Enough Information')),
        reason TEXT NOT NULL,
        contract_evidence TEXT,
        standard_id TEXT,
        standard_text TEXT,
        source TEXT NOT NULL CHECK (source IN ('rule_engine', 'rule_engine+llm')),
        status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'marked_for_review')),
        reviewer_note TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
        FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE SET NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_contract ON reviews (contract_id);")

    # Create questions table
    cursor.execute("""
    CREATE TABLE questions (
        id TEXT PRIMARY KEY,
        contract_id TEXT NOT NULL,
        question TEXT NOT NULL,
        category TEXT NOT NULL,
        FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_contract ON questions (contract_id);")

    # Create rules table
    cursor.execute("""
    CREATE TABLE rules (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        parameter_name TEXT,
        operator TEXT,
        value TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        reason TEXT NOT NULL
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_category ON rules (category);")
    
    conn.commit()
    conn.close()


