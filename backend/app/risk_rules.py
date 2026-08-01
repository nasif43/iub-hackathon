from backend.app.facts import (
    parse_payment_clause,
    parse_termination_clause,
    parse_renewal_clause,
    parse_data_protection_clause,
    parse_confidentiality_clause,
    parse_ip_clause,
    parse_liability_clause
)

def evaluate_payment(text: str) -> tuple[str, dict, str]:
    facts, source = parse_payment_clause(text)
    
    # Check Shape B first
    if facts["payment_structure"] == "100% prepayment":
        return "High Risk", facts, source
    if facts["payment_structure"] == "50/50 split":
        return "Medium Risk", facts, source
        
    # Check Shape A
    days = facts["days_to_pay"]
    if days is not None:
        if days >= 30:
            risk = "Low Risk"
        elif 15 <= days <= 29:
            risk = "Medium Risk"
        else:
            risk = "High Risk"
            
        # Any late fee > 1% (or 12% annual which is 1% monthly) triggers High Risk
        fee = facts["late_fee_percent"]
        if fee is not None and fee > 1.0:
            risk = "High Risk"
            
        return risk, facts, source
        
    return "Medium Risk", facts, source # default fallback if clause exists but shape unparsed

def evaluate_termination(text: str) -> tuple[str, dict, str]:
    facts, source = parse_termination_clause(text)
    
    # Grounds check
    if facts["grounds"]["vendor"] == "convenience" and facts["grounds"]["customer"] == "breach":
        return "High Risk", facts, source
        
    # Cure rights check
    if not facts["cure_present"] or facts["cure_days"] == 0:
        return "High Risk", facts, source
        
    # Notice period check
    notice = facts["notice_days"]
    if notice is not None:
        if notice == 30:
            return "Low Risk", facts, source
        elif notice >= 90:
            return "High Risk", facts, source
        else:
            return "Medium Risk", facts, source
            
    return "Low Risk", facts, source

def evaluate_renewal(text: str) -> tuple[str, dict, str]:
    facts, source = parse_renewal_clause(text)
    months = facts["renewal_months"]
    notice = facts["notice_days"]
    
    if months is None and notice is None:
        return "Low Risk", facts, source
        
    m_val = months if months is not None else 12
    n_val = notice if notice is not None else 30
    
    if m_val >= 24 or n_val >= 60:
        return "High Risk", facts, source
    if m_val > 12 and n_val > 30:
        return "High Risk", facts, source
    if m_val > 12 or n_val > 30:
        return "Medium Risk", facts, source
        
    return "Low Risk", facts, source


def evaluate_data_protection(text: str) -> tuple[str, dict, str]:
    facts, source = parse_data_protection_clause(text)
    
    violations = 0
    if not facts["encryption_at_rest"]:
        violations += 1
    if facts["breach_notice_hours"] is not None and facts["breach_notice_hours"] > 48:
        violations += 1
    if not facts["subprocessor_approval"]:
        violations += 1
    if facts["deletion_days"] is not None and facts["deletion_days"] > 30:
        violations += 1
        
    if violations >= 3:
        return "High Risk", facts, source
    elif violations >= 1:
        return "Medium Risk", facts, source
    return "Low Risk", facts, source

def evaluate_confidentiality(text: str) -> tuple[str, dict, str]:
    facts, source = parse_confidentiality_clause(text)
    
    if not facts["reciprocal"]:
        return "High Risk", facts, source
        
    duration = facts["duration_years"]
    carve_outs = facts["carve_outs_present"]
    
    if duration is None:
        return "High Risk", facts, source
        
    if duration < 3 and not carve_outs:
        return "High Risk", facts, source
    if duration < 3 or not carve_outs:
        if duration < 3:
            return "Medium Risk" if carve_outs else "High Risk", facts, source
        else:
            return "Medium Risk", facts, source
            
    return "Low Risk", facts, source

def evaluate_ip(text: str) -> tuple[str, dict, str]:
    facts, source = parse_ip_clause(text)
    
    if not facts["customer_owns_custom"] or not facts["licence_permanent"]:
        return "High Risk", facts, source
        
    return "Low Risk", facts, source

def evaluate_liability(text: str) -> tuple[str, dict, str]:
    facts, source = parse_liability_clause(text)
    
    if facts["asymmetric"]:
        return "High Risk", facts, source
    if facts["cap_months"] is not None and facts["cap_months"] < 12:
        return "High Risk", facts, source
    if not facts["carve_outs_present"]:
        return "Medium Risk", facts, source
        
    return "Low Risk", facts, source

EVALUATORS = {
    "Payment": evaluate_payment,
    "Termination": evaluate_termination,
    "Automatic Renewal": evaluate_renewal,
    "Data Protection": evaluate_data_protection,
    "Confidentiality": evaluate_confidentiality,
    "Intellectual Property": evaluate_ip,
    "Limitation of Liability": evaluate_liability
}

def evaluate_risk(category: str, text: str | None) -> tuple[str, dict | None, str]:
    """
    Computes risk level and returns (risk_level, facts, source).
    If text is None (category absent), returns ('Not Enough Information', None, 'rule_engine')
    """
    if text is None:
        return "Not Enough Information", None, "rule_engine"
        
    evaluator = EVALUATORS.get(category)
    if evaluator:
        return evaluator(text)
        
    return "Not Enough Information", None, "rule_engine"
