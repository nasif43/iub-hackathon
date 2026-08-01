import re

def extract_number_from_text(text: str, keywords: list[str]) -> int | None:
    """
    Looks for a pattern: number followed by a keyword (e.g., '30 days', '12 months', '48 hours')
    """
    text_lower = text.lower()
    for kw in keywords:
        # e.g., "30 days" or "30 calendar days" or "30 business days" or "12-month"
        pattern = rf"(\d+)\s*(?:calendar|business|-)?\s*{re.escape(kw)}"
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))
            
        # Or keyword followed by number (less common, but let's be robust)
        pattern_rev = rf"{re.escape(kw)}\s*(\d+)"
        match_rev = re.search(pattern_rev, text_lower)
        if match_rev:
            return int(match_rev.group(1))

            
    # Fallback to any standalone number near keyword
    for kw in keywords:
        if kw in text_lower:
            # find all numbers in the text
            numbers = re.findall(r"\b\d+\b", text_lower)
            if len(numbers) == 1:
                return int(numbers[0])
                
    return None

def extract_percent(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if match:
        return float(match.group(1))
    return None

def parse_payment_clause(text: str) -> dict:
    """
    Returns a dict with:
    - days_to_pay: int | None
    - payment_structure: str | None (prepayment, split, etc.)
    - late_fee_percent: float | None
    """
    res = {
        "days_to_pay": None,
        "payment_structure": None,
        "late_fee_percent": None
    }
    
    # Check late fee percent per month
    pct = extract_percent(text)
    if pct is not None and ("late" in text.lower() or "interest" in text.lower() or "fee" in text.lower()):
        res["late_fee_percent"] = pct

    # Check for payment structure shapes (Shape B)
    text_lower = text.lower()
    if "100%" in text_lower and ("before" in text_lower or "prepayment" in text_lower or "begins" in text_lower or "prior to" in text_lower):
        res["payment_structure"] = "100% prepayment"
    elif "50%" in text_lower and "before" in text_lower and "50%" in text_lower and "after" in text_lower:
        res["payment_structure"] = "50/50 split"
    elif "before" in text_lower and "campaign begins" in text_lower:
        res["payment_structure"] = "100% prepayment"
        
    # Check for Shape A: days count
    days = extract_number_from_text(text, ["day", "days"])
    if days is not None:
        res["days_to_pay"] = days
        
    return res

def parse_termination_clause(text: str) -> dict:
    """
    Returns:
    - notice_days: int | None
    - cure_days: int | None
    - grounds: dict with "vendor" and "customer" keys, values being convenince/breach
    - cure_present: bool
    """
    res = {
        "notice_days": None,
        "cure_days": None,
        "cure_present": True,
        "grounds": {
            "vendor": "convenience", # default if not specified
            "customer": "convenience"
        }
    }
    
    text_lower = text.lower()
    
    # Notice days for convenience
    notice = extract_number_from_text(text, ["day's notice", "days notice", "days' notice", "days written notice", "days notice", "day notice"])
    if notice is None:
        notice = extract_number_from_text(text, ["day", "days"])
    res["notice_days"] = notice
    
    # Cure period for breach
    cure = extract_number_from_text(text, ["days to fix", "days to cure", "day cure", "days cure", "day cure period", "days cure period", "day to fix", "days to fix the problem", "material breach that remains unfixed for"])
    if cure is None:
        # Check if text says "immediate" or "does not have a right to fix"
        if "no right to fix" in text_lower or "does not have a right to fix" in text_lower or "immediately after any breach" in text_lower or "immediate termination" in text_lower:
            res["cure_present"] = False
            res["cure_days"] = 0
    else:
        res["cure_days"] = cure
        
    # Grounds check
    # Check asymmetric grounds:
    # Vendor termination convenience vs customer breach only
    # E.g. "NovaStaff may terminate ... for any reason ... Customer may terminate only for a material breach"
    if "novastaff may terminate" in text_lower or "vendor may terminate" in text_lower or "either party may terminate" not in text_lower:
        # Let's inspect parts of the sentence
        if "for any reason" in text_lower or "for convenience" in text_lower:
            # If it restricts the Customer/Customer may terminate only:
            if "customer may terminate only" in text_lower or "customer may terminate only for a material breach" in text_lower or "customer may terminate only for breach" in text_lower:
                res["grounds"]["vendor"] = "convenience"
                res["grounds"]["customer"] = "breach"
                
    return res

def parse_renewal_clause(text: str) -> dict:
    """
    Returns:
    - renewal_months: int | None
    - notice_days: int | None
    """
    res = {
        "renewal_months": None,
        "notice_days": None
    }
    months = extract_number_from_text(text, ["month term", "months term", "month period", "months period", "month", "months"])
    res["renewal_months"] = months
    
    notice = extract_number_from_text(text, ["days before", "days' notice", "days notice", "days written notice"])
    res["notice_days"] = notice
    
    return res

def parse_data_protection_clause(text: str) -> dict:
    """
    Returns:
    - encryption_at_rest: bool
    - breach_notice_hours: int | None
    - subprocessor_approval: bool
    - deletion_days: int | None
    """
    text_lower = text.lower()
    res = {
        "encryption_at_rest": True,
        "breach_notice_hours": None,
        "subprocessor_approval": True,
        "deletion_days": None
    }
    
    # Encryption at rest
    if "encryption of stored data is not required" in text_lower or "no encryption at rest" in text_lower:
        res["encryption_at_rest"] = False
        
    # Breach notice hours
    hours = extract_number_from_text(text, ["hour", "hours"])
    res["breach_notice_hours"] = hours
    
    # Subprocessor approval
    if "without prior approval" in text_lower or "no prior approval" in text_lower or "does not require prior approval" in text_lower:
        res["subprocessor_approval"] = False
        
    # Deletion window
    days = extract_number_from_text(text, ["days after the service ends", "days after termination", "days"])
    res["deletion_days"] = days
    
    return res

def parse_confidentiality_clause(text: str) -> dict:
    """
    Returns:
    - duration_years: int | None
    - carve_outs_present: bool
    - reciprocal: bool
    """
    text_lower = text.lower()
    res = {
        "duration_years": None,
        "carve_outs_present": True,
        "reciprocal": True
    }
    
    # Duration
    years = extract_number_from_text(text, ["year", "years"])
    res["duration_years"] = years
    
    # Carve outs
    if "public" not in text_lower and "previously known" not in text_lower and "independently developed" not in text_lower and "exclud" not in text_lower:
        res["carve_outs_present"] = False
        
    # Reciprocal
    if "customer must protect" in text_lower and "novastaff has no confidentiality duty" in text_lower:
        res["reciprocal"] = False
        
    return res

def parse_ip_clause(text: str) -> dict:
    """
    Returns:
    - customer_owns_custom: bool
    - licence_permanent: bool
    """
    text_lower = text.lower()
    res = {
        "customer_owns_custom": True,
        "licence_permanent": True
    }
    
    if "novastaff owns all" in text_lower or "marketloop owns all" in text_lower or "vendor owns" in text_lower:
        res["customer_owns_custom"] = False
        
    if "six months" in text_lower or "usable only while this agreement remains active" in text_lower or "temporary licence" in text_lower:
        res["licence_permanent"] = False
        
    return res

def parse_liability_clause(text: str) -> dict:
    """
    Returns:
    - cap_months: int | None
    - asymmetric: bool
    - carve_outs_present: bool
    """
    text_lower = text.lower()
    res = {
        "cap_months": 12, # default
        "asymmetric": False,
        "carve_outs_present": True
    }
    
    if "one month" in text_lower:
        res["cap_months"] = 1
        
    if "customer has unlimited liability" in text_lower or "asymmetric liability" in text_lower:
        res["asymmetric"] = True
        
    if "gross negligence" not in text_lower and "fraud" not in text_lower:
        res["carve_outs_present"] = False
        
    return res
