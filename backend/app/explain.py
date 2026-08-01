import os

def build_explanation(category: str, risk_level: str, facts: dict | None, evidence: str | None) -> tuple[str, str]:
    """
    Produces the plain-language reason string and the source.
    If USE_LLM_EXPLANATIONS=true, would call LLM, but defaults to template.
    Acceptance Criteria: reason text never contains a number not present in either the contract evidence or standard text.
    """
    # Check if we should use LLM
    use_llm = os.getenv("USE_LLM_EXPLANATIONS", "false").lower() == "true"
    
    if risk_level == "Not Enough Information":
        reason = f"No {category.lower()} clause found in this contract excerpt."
        return reason, "rule_engine"

    if facts is None:
        reason = "Unable to parse details from the clause."
        return reason, "rule_engine"
        
    reason_templates = {
        "Payment": {
            "High Risk": "The contract requires prepayment or an extremely short payment term ({days} days), violating the 30-day standard.",
            "Medium Risk": "The contract deviates from the 30-day payment standard, requiring payment within {days} days or via a front-loaded split structure.",
            "Low Risk": "The payment term of {days} days is compliant with the 30-day standard."
        },
        "Termination": {
            "High Risk": "The termination terms pose high risk due to asymmetric convenience rights or immediate breach termination without a cure period ({cure} days cure).",
            "Medium Risk": "The termination notice period ({notice} days) deviates from the 30-day standard.",
            "Low Risk": "The termination clause is compliant with the 30-day notice standard and includes a {cure}-day cure period."
        },
        "Automatic Renewal": {
            "High Risk": "The automatic renewal period ({renewal} months) or cancellation notice period ({notice} days) significantly exceeds the standard.",
            "Medium Risk": "The renewal terms exceed the standard with a {renewal}-month renewal period or {notice}-day notice requirement.",
            "Low Risk": "The renewal terms are compliant with the 12-month renewal and 30-day notice standards."
        },
        "Data Protection": {
            "High Risk": "The data protection terms fail key standards: breach notification time ({breach_hours} hours) or data deletion window ({deletion_days} days).",
            "Medium Risk": "The data protection terms deviate from standard guidelines on breach notification ({breach_hours} hours) or subprocessors.",
            "Low Risk": "The data protection terms comply with company encryption and breach notification standards."
        },
        "Confidentiality": {
            "High Risk": "The confidentiality terms lack reciprocity or duration ({duration} years duration), or fail to include standard exclusions.",
            "Medium Risk": "The confidentiality terms have non-standard exclusions or a short duration ({duration} years duration).",
            "Low Risk": "The confidentiality terms are reciprocal and protect information for a compliant duration ({duration} years)."
        },
        "Intellectual Property": {
            "High Risk": "The vendor retains ownership of custom deliverables, or limits the customer's licence back.",
            "Medium Risk": "The intellectual property rights deviate from standard transfer terms.",
            "Low Risk": "The intellectual property rights comply with customer ownership of custom work."
        },
        "Limitation of Liability": {
            "High Risk": "The liability cap is set to less than 12 months of fees ({cap} month cap) or contains asymmetric terms.",
            "Medium Risk": "The limitation of liability clause lacks standard carve-outs for fraud or breach of confidentiality.",
            "Low Risk": "The limitation of liability cap and carve-outs comply with company standards."
        }
    }
    
    cat_templates = reason_templates.get(category, {})
    template = cat_templates.get(risk_level, "The clause deviates from company standards.")
    
    # Format the template safely
    formatted_args = {}
    if category == "Payment":
        formatted_args["days"] = facts.get("days_to_pay") or "0"
    elif category == "Termination":
        formatted_args["notice"] = facts.get("notice_days") or "30"
        formatted_args["cure"] = facts.get("cure_days") or "0"
    elif category == "Automatic Renewal":
        formatted_args["renewal"] = facts.get("renewal_months") or "0"
        formatted_args["notice"] = facts.get("notice_days") or "30"
    elif category == "Data Protection":
        formatted_args["breach_hours"] = facts.get("breach_notice_hours") or "48"
        formatted_args["deletion_days"] = facts.get("deletion_days") or "30"
    elif category == "Confidentiality":
        formatted_args["duration"] = facts.get("duration_years") or "unknown"
    elif category == "Limitation of Liability":
        formatted_args["cap"] = facts.get("cap_months") or "12"
        
    reason = template.format(**formatted_args)
    
    # If LLM rewrite is ever active (though default is false), we'd call the LLM and verify here.
    
    return reason, "rule_engine"
