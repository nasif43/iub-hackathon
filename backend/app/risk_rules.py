from backend.app.facts import (
    parse_payment_clause,
    parse_termination_clause,
    parse_renewal_clause,
    parse_data_protection_clause,
    parse_confidentiality_clause,
    parse_ip_clause,
    parse_liability_clause
)

def evaluate_payment(text: str) -> tuple[str, dict]:
    facts = parse_payment_clause(text)
    
    # Check Shape B first
    if facts["payment_structure"] == "100% prepayment":
        return "High Risk", facts
    if facts["payment_structure"] == "50/50 split":
        return "Medium Risk", facts
        
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
            
        return risk, facts
        
    return "Medium Risk", facts # default fallback if clause exists but shape unparsed

def evaluate_termination(text: str) -> tuple[str, dict]:
    facts = parse_termination_clause(text)
    
    # Grounds check
    if facts["grounds"]["vendor"] == "convenience" and facts["grounds"]["customer"] == "breach":
        return "High Risk", facts
        
    # Cure rights check
    if not facts["cure_present"] or facts["cure_days"] == 0:
        return "High Risk", facts
        
    if facts["cure_days"] is not None and facts["cure_days"] > 10:
        # standard is 10 business days. If it's more e.g. 30 days, that is higher cure time (favors breaching party)
        # But wait, 30 days is common. Let's see: C-002 has 30 days (but that's asymmetric anyway).
        pass
        
    # Notice period check
    notice = facts["notice_days"]
    if notice is not None:
        if notice == 30:
            return "Low Risk", facts
        elif notice >= 90: # Magnitude >= 2x standard (double standard 30 is 60, 90 is 3x)
            return "High Risk", facts
        else:
            return "Medium Risk", facts
            
    return "Low Risk", facts

def evaluate_renewal(text: str) -> tuple[str, dict]:
    facts = parse_renewal_clause(text)
    months = facts["renewal_months"]
    notice = facts["notice_days"]
    
    if months is None and notice is None:
    # If present but can't find renewal facts, it's not a complete match, but let's see.
        return "Low Risk", facts
        
    # Standard: renewal length <= 12 months, notice-to-cancel <= 30 days
    # Both within standard -> Low Risk
    # One dimension exceeds standard -> Medium Risk
    # Both dimensions exceed standard, or at least one is >= 2x standard (24mo, 60+ days notice) -> High Risk
    m_val = months if months is not None else 12
    n_val = notice if notice is not None else 30
    
    if m_val >= 24 or n_val >= 60:
        return "High Risk", facts
    if m_val > 12 and n_val > 30:
        return "High Risk", facts
    if m_val > 12 or n_val > 30:
        return "Medium Risk", facts
        
    return "Low Risk", facts


def evaluate_data_protection(text: str) -> tuple[str, dict]:
    facts = parse_data_protection_clause(text)
    
    # Score based on how many rules it violates
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
        return "High Risk", facts
    elif violations >= 1:
        return "Medium Risk", facts
    return "Low Risk", facts

def evaluate_confidentiality(text: str) -> tuple[str, dict]:
    facts = parse_confidentiality_clause(text)
    
    # Standard: duration >= 3 years; carve-outs present; reciprocity.
    # missing carve-outs as its own risk contributor:
    # C-007 (1-year duration, no carve-outs) -> High Risk
    # C-008 (3-year duration, no carve-outs) -> Medium Risk
    # C-002 (one-sided, no duration) -> High Risk
    
    if not facts["reciprocal"]:
        return "High Risk", facts
        
    duration = facts["duration_years"]
    carve_outs = facts["carve_outs_present"]
    
    if duration is None: # missing duration
        return "High Risk", facts
        
    if duration < 3 and not carve_outs:
        return "High Risk", facts
    if duration < 3 or not carve_outs:
        if duration < 3:
            # check if also missing carve_outs
            return "Medium Risk" if carve_outs else "High Risk", facts
        else: # duration >= 3 but missing carve_outs
            return "Medium Risk", facts
            
    return "Low Risk", facts

def evaluate_ip(text: str) -> tuple[str, dict]:
    facts = parse_ip_clause(text)
    
    # High Risk if vendor retains all ownership (C-002, C-005)
    if not facts["customer_owns_custom"] or not facts["licence_permanent"]:
        return "High Risk", facts
        
    return "Low Risk", facts

def evaluate_liability(text: str) -> tuple[str, dict]:
    facts = parse_liability_clause(text)
    
    # Cap window vs 12 months of fees; carve-outs present?
    # Shorter cap window (C-001: one month) -> High Risk
    # Asymmetric liability (C-005: customer unlimited, vendor capped) -> High Risk
    # C-007 has 12-month cap but zero carve-outs -> Medium Risk
    
    if facts["asymmetric"]:
        return "High Risk", facts
    if facts["cap_months"] is not None and facts["cap_months"] < 12:
        return "High Risk", facts
    if not facts["carve_outs_present"]:
        return "Medium Risk", facts
        
    return "Low Risk", facts

EVALUATORS = {
    "Payment": evaluate_payment,
    "Termination": evaluate_termination,
    "Automatic Renewal": evaluate_renewal,
    "Data Protection": evaluate_data_protection,
    "Confidentiality": evaluate_confidentiality,
    "Intellectual Property": evaluate_ip,
    "Limitation of Liability": evaluate_liability
}

def evaluate_risk(category: str, text: str | None) -> tuple[str, dict | None]:
    """
    Computes risk level and returns facts.
    If text is None (category absent), returns 'Not Enough Information'
    """
    if text is None:
        return "Not Enough Information", None
        
    evaluator = EVALUATORS.get(category)
    if evaluator:
        return evaluator(text)
        
    return "Not Enough Information", None
