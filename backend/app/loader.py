import os
import json
import re
from backend.app.db import get_db_connection, init_db
from backend.app.segmenter import segment_contract
from backend.app.classifier import classify_clause, CATEGORIES

def load_all_data(raw_data_dir: str = "./data/raw"):
    # Initialize the DB schema
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Load Standards
    standards_path = os.path.join(raw_data_dir, "company_standards.json")
    with open(standards_path, "r", encoding="utf-8") as f:
        standards = json.load(f)
        
    for std in standards:
        cursor.execute(
            "INSERT OR REPLACE INTO standards (id, category, text) VALUES (?, ?, ?);",
            (std["id"], std["category"], std["standard"])
        )
        
    # 2. Parse and Load Contracts
    for filename in sorted(os.listdir(raw_data_dir)):
        if filename.startswith("C-") and filename.endswith(".txt"):
            file_path = os.path.join(raw_data_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Parse header fields
            contract_id = filename.replace(".txt", "")
            
            title_match = re.search(r"Title:\s*(.+)", content)
            title = title_match.group(1).strip() if title_match else "Unknown Title"
            
            parties_match = re.search(r"Parties:\s*(.+)", content)
            parties = parties_match.group(1).strip() if parties_match else "Unknown Parties"
            
            # Find Dataset Note if any
            dataset_note = None
            note_match = re.search(r"Dataset Note:\s*(.+)", content, re.DOTALL)
            if note_match:
                dataset_note = note_match.group(1).strip()
                
            cursor.execute(
                "INSERT OR REPLACE INTO contracts (id, title, parties, raw_text, dataset_note) VALUES (?, ?, ?, ?, ?);",
                (contract_id, title, parties, content, dataset_note)
            )
            
            # Segment the contract
            blocks = segment_contract(content)
            
            # Map found blocks to categories (accumulate text if multiple blocks map to the same category, like C-003 Data Protection)
            found_clauses = {}
            for heading, body in blocks:
                cat = classify_clause(heading, body)
                if cat:
                    if cat not in found_clauses:
                        found_clauses[cat] = {"headings": [heading], "bodies": [body]}
                    else:
                        found_clauses[cat]["headings"].append(heading)
                        found_clauses[cat]["bodies"].append(body)
            
            # Insert clauses for all 7 categories
            for cat in CATEGORIES:
                if cat in found_clauses:
                    heading_str = " / ".join(found_clauses[cat]["headings"])
                    body_str = "\n\n".join(found_clauses[cat]["bodies"])
                    cursor.execute(
                        "INSERT INTO clauses (contract_id, category, heading, text, present) VALUES (?, ?, ?, ?, 1);",
                        (contract_id, cat, heading_str, body_str)
                    )

                else:
                    cursor.execute(
                        "INSERT INTO clauses (contract_id, category, heading, text, present) VALUES (?, ?, NULL, NULL, 0);",
                        (contract_id, cat)
                    )
                    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    load_all_data()
    print("Database loaded successfully.")
