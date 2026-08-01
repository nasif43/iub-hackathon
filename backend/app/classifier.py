def get_dynamic_categories() -> list[str]:
    try:
        from backend.app.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM standards;")
        rows = cursor.fetchall()
        conn.close()
        categories = [row["category"] for row in rows]
        if categories:
            # Preserve ordering if they include the standard 7
            defaults = [
                "Payment",
                "Termination",
                "Data Protection",
                "Confidentiality",
                "Automatic Renewal",
                "Intellectual Property",
                "Limitation of Liability"
            ]
            # Merge and preserve order
            merged = []
            for d in defaults:
                if d in categories:
                    merged.append(d)
            for c in categories:
                if c not in merged:
                    merged.append(c)
            return merged
    except Exception:
        pass
    return [
        "Payment",
        "Termination",
        "Data Protection",
        "Confidentiality",
        "Automatic Renewal",
        "Intellectual Property",
        "Limitation of Liability"
    ]

# We dynamicize CATEGORIES by defining it as a property/list-like proxy or just a dynamic list getter,
# but since it's imported at module-level in loader.py, let's make it a subclass of list that evaluates dynamically.
class DynamicCategoriesList(list):
    def __iter__(self):
        return iter(get_dynamic_categories())
    def __len__(self):
        return len(get_dynamic_categories())
    def __contains__(self, item):
        return item in get_dynamic_categories()

CATEGORIES = DynamicCategoriesList()

# Keywords config-driven checked against heading first, fallback to body
CLASSIFICATION_RULES = {
    "Payment": {
        "heading": ["payment", "fee", "invoice", "price", "billing"],
        "body": ["pay", "invoice", "billing", "fee", "prepayment", "deposit"]
    },
    "Termination": {
        "heading": ["termination", "terminate", "end the agreement", "cancellation"],
        "body": ["terminate", "termination", "notice to cancel", "cure period", "material breach"]
    },
    "Data Protection": {
        "heading": ["data protection", "security", "privacy", "personal data", "breach notice", "subprocessor", "dpa", "use of data"],
        "body": ["personal data", "encrypt", "data breach", "subprocessor", "gdpr", "breach notification"]
    },
    "Confidentiality": {
        "heading": ["confidentiality", "confidential", "non-disclosure", "nda"],
        "body": ["confidential information", "protect information", "disclosure", "exclusions", "carve-out"]
    },
    "Automatic Renewal": {
        "heading": ["automatic renewal", "renewal", "renew"],
        "body": ["automatically renews", "renewal period", "notice to stop renewal", "extension"]
    },
    "Intellectual Property": {
        "heading": ["intellectual property", "ip", "ownership", "proprietary", "patent", "copyright", "deliverables"],
        "body": ["owns", "ownership", "licence", "license", "intellectual property", "deliverables", "pre-existing"]
    },
    "Limitation of Liability": {
        "heading": ["limitation of liability", "liability", "liability cap", "indemnification", "damages"],
        "body": ["liability", "limited to", "cap", "consequential damages", "exceed", "indemnify"]
    }
}


def classify_clause(heading: str, body: str) -> str | None:
    """
    Classify a (heading, body) block into one of the categories.
    """
    h_lower = heading.lower()
    b_lower = body.lower()
    
    categories = get_dynamic_categories()
    
    # Build dynamic classification rules for custom categories
    rules_dict = dict(CLASSIFICATION_RULES)
    for cat in categories:
        if cat not in rules_dict:
            # Generate generic keywords based on the category name itself
            clean_name = cat.lower().replace("-", " ").replace("_", " ")
            words = [w for w in clean_name.split() if len(w) > 2]
            rules_dict[cat] = {
                "heading": [clean_name] + words,
                "body": [clean_name] + words
            }
            
    # Try heading first
    for category in categories:
        rules = rules_dict.get(category, {"heading": [], "body": []})
        for kw in rules["heading"]:
            if kw in h_lower:
                return category
                
    # Fallback to body
    for category in categories:
        rules = rules_dict.get(category, {"heading": [], "body": []})
        for kw in rules["body"]:
            if kw in b_lower:
                return category
                
    return None

