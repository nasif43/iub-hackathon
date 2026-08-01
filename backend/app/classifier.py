CATEGORIES = [
    "Payment",
    "Termination",
    "Data Protection",
    "Confidentiality",
    "Automatic Renewal",
    "Intellectual Property",
    "Limitation of Liability"
]

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
    Classify a (heading, body) block into one of the 7 fixed categories using rules.
    Returns the category name, or None if it doesn't match any.
    """
    h_lower = heading.lower()
    b_lower = body.lower()
    
    # Try heading first
    for category, rules in CLASSIFICATION_RULES.items():
        for kw in rules["heading"]:
            if kw in h_lower:
                return category
                
    # Fallback to body
    for category, rules in CLASSIFICATION_RULES.items():
        for kw in rules["body"]:
            if kw in b_lower:
                return category
                
    return None
