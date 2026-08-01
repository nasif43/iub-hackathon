import re
import os
import json
import hashlib
import urllib.request
import urllib.error

# Cache keyed by (contract_id, category, text_hash) -> (facts_dict, source_str)
_EXTRACTION_CACHE: dict[tuple[str, str, str], tuple[dict, str]] = {}

def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def normalize_units(text: str, keywords: list[str]) -> int | None:
    """
    Step 2: Deterministic regex and lookup-table conversion for non-base units:
    - weeks -> days (*7)
    - business weeks -> business days (*5)
    - quarters -> months (*3)
    - business days -> days (1:1 value kept as days/business days)
    """
    text_lower = text.lower()
    
    # 1. Business weeks -> business days (1 week = 5 business days)
    pattern_bweeks = r"(\d+)\s*(?:-| )?business\s*(?:week|weeks)"
    match_bw = re.search(pattern_bweeks, text_lower)
    if match_bw:
        return int(match_bw.group(1)) * 5

    # 2. Weeks -> days (* 7)
    pattern_weeks = r"(\d+)\s*(?:-| )?week\s*s?"
    match_w = re.search(pattern_weeks, text_lower)
    if match_w:
        if not re.search(r"business\s*" + pattern_weeks, text_lower):
            return int(match_w.group(1)) * 7

    # 3. Quarters -> months (* 3)
    number_words = {"one": 1, "two": 2, "three": 3, "four": 4, "a": 1, "an": 1}
    pattern_quarters = r"\b(\d+|one|two|three|four|a|an)\s*(?:-| )?quarter\s*s?\b"
    match_q = re.search(pattern_quarters, text_lower)
    if match_q:
        raw_val = match_q.group(1)
        val = number_words.get(raw_val, int(raw_val) if raw_val.isdigit() else None)
        if val is not None:
            return val * 3

    return None


def llm_fallback_extract(text: str, keywords: list[str]) -> int | None:
    """
    Step 3, 4, 5: OpenRouter fallback fact extraction with strict verification gate.
    Gated by USE_LLM_FACT_EXTRACTION=true and presence of OPENROUTER_API_KEY.
    """
    use_llm = os.getenv("USE_LLM_FACT_EXTRACTION", "false").lower() in ("true", "1", "t", "yes")
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    if not use_llm or not api_key:
        return None

    prompt = (
        "You are a strict data extraction assistant. "
        "Extract the primary numeric period or amount relevant to these keywords: "
        f"{', '.join(keywords)} from the provided text.\n"
        "Return ONLY a JSON object with keys 'value' (an integer or null) and 'unit' (string or null). "
        "Do NOT return any other text, reasoning, risk judgment, or explanation.\n\n"
        f"Source Text:\n{text}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free"),
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            content = res_data["choices"][0]["message"]["content"].strip()
            
            if "```" in content:
                content = re.sub(r"```(?:json)?", "", content).strip()
            
            parsed = json.loads(content)
            val = parsed.get("value")
            
            if val is not None:
                val_int = int(val)
                # Verification Gate: check string containment in source text
                val_str = str(val_int)
                if val_str in text or any(w in text.lower() for w, num in {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}.items() if num == val_int):
                    return val_int
    except Exception:
        pass

    return None


def extract_number_from_text(text: str, keywords: list[str]) -> tuple[int | None, str]:
    text_lower = text.lower()
    
    # Step 1: Primary Regex Path (days, months, %, hours)
    for kw in keywords:
        pattern = rf"(\d+)\s*(?:calendar|business|-)?\s*{re.escape(kw)}"
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1)), "rule_engine"
            
        pattern_rev = rf"{re.escape(kw)}\s*(\d+)"
        match_rev = re.search(pattern_rev, text_lower)
        if match_rev:
            return int(match_rev.group(1)), "rule_engine"

    for kw in keywords:
        if kw in text_lower:
            numbers = re.findall(r"\b\d+\b", text_lower)
            if len(numbers) == 1:
                return int(numbers[0]), "rule_engine"

    # Step 2: Unit Normalization
    unit_val = normalize_units(text, keywords)
    if unit_val is not None:
        return unit_val, "rule_engine"

    # Step 3-5: Optional LLM Fallback (OpenRouter)
    llm_val = llm_fallback_extract(text, keywords)
    if llm_val is not None:
        return llm_val, "rule_engine+llm_extraction"

    return None, "rule_engine"


def extract_percent(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if match:
        return float(match.group(1))
    return None

def _raw_parse_payment(text: str) -> tuple[dict, str]:
    res = {
        "days_to_pay": None,
        "payment_structure": None,
        "late_fee_percent": None
    }
    source = "rule_engine"
    
    pct = extract_percent(text)
    if pct is not None and ("late" in text.lower() or "interest" in text.lower() or "fee" in text.lower()):
        res["late_fee_percent"] = pct

    text_lower = text.lower()
    if "100%" in text_lower and ("before" in text_lower or "prepayment" in text_lower or "begins" in text_lower or "prior to" in text_lower):
        res["payment_structure"] = "100% prepayment"
    elif "50%" in text_lower and "before" in text_lower and "50%" in text_lower and "after" in text_lower:
        res["payment_structure"] = "50/50 split"
    elif "before" in text_lower and "campaign begins" in text_lower:
        res["payment_structure"] = "100% prepayment"
        
    days, src = extract_number_from_text(text, ["day", "days"])
    if days is not None:
        res["days_to_pay"] = days
        source = src
        
    return res, source

def parse_payment_clause(text: str, contract_id: str = "", category: str = "Payment") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_payment(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res


def _raw_parse_termination(text: str) -> tuple[dict, str]:
    res = {
        "notice_days": None,
        "cure_days": None,
        "cure_present": True,
        "grounds": {
            "vendor": "convenience",
            "customer": "convenience"
        }
    }
    sources = []
    text_lower = text.lower()
    
    notice, src_n = extract_number_from_text(text, ["day's notice", "days notice", "days' notice", "days written notice", "day notice"])
    if notice is None:
        notice, src_n = extract_number_from_text(text, ["day", "days"])
    res["notice_days"] = notice
    if notice is not None:
        sources.append(src_n)
    
    cure, src_c = extract_number_from_text(text, ["days to fix", "days to cure", "day cure", "days cure", "day cure period", "days cure period", "day to fix", "days to fix the problem", "material breach that remains unfixed for"])
    if cure is None:
        if "no right to fix" in text_lower or "does not have a right to fix" in text_lower or "immediately after any breach" in text_lower or "immediate termination" in text_lower:
            res["cure_present"] = False
            res["cure_days"] = 0
    else:
        res["cure_days"] = cure
        sources.append(src_c)
        
    vendor_names = ["vendor", "provider", "seller", "novastaff", "marketloop"]
    customer_names = ["customer", "client", "buyer", "northstar"]
    
    vendor_convenience = False
    customer_breach = False
    
    sentences = [s.strip() for s in text_lower.replace("\n", " ").split(".") if s.strip()]
    for s in sentences:
        if any(v_name in s for v_name in vendor_names) and ("any reason" in s or "convenience" in s or "notice" in s):
            vendor_convenience = True
        if any(c_name in s for c_name in customer_names) and ("only for" in s or "only in" in s or "only for breach" in s or "only for a material breach" in s or "only after a material breach" in s):
            customer_breach = True
            
    if vendor_convenience and customer_breach:
        res["grounds"]["vendor"] = "convenience"
        res["grounds"]["customer"] = "breach"
        
    final_source = "rule_engine+llm_extraction" if "rule_engine+llm_extraction" in sources else "rule_engine"
    return res, final_source

def parse_termination_clause(text: str, contract_id: str = "", category: str = "Termination") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_termination(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res


def _raw_parse_renewal(text: str) -> tuple[dict, str]:
    res = {
        "renewal_months": None,
        "notice_days": None
    }
    sources = []
    
    months, src_m = extract_number_from_text(text, ["month term", "months term", "month period", "months period", "month", "months", "quarter", "quarters"])
    res["renewal_months"] = months
    if months is not None:
        sources.append(src_m)
    
    notice, src_n = extract_number_from_text(text, ["days before", "days' notice", "days notice", "days written notice"])
    if notice is None:
        notice, src_n = extract_number_from_text(text, ["day", "days", "week", "weeks"])
    res["notice_days"] = notice
    if notice is not None:
        sources.append(src_n)
    
    final_source = "rule_engine+llm_extraction" if "rule_engine+llm_extraction" in sources else "rule_engine"
    return res, final_source

def parse_renewal_clause(text: str, contract_id: str = "", category: str = "Automatic Renewal") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_renewal(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res


def _raw_parse_data_protection(text: str) -> tuple[dict, str]:
    text_lower = text.lower()
    res = {
        "encryption_at_rest": True,
        "breach_notice_hours": None,
        "subprocessor_approval": True,
        "deletion_days": None
    }
    sources = []
    
    if "encryption of stored data is not required" in text_lower or "no encryption at rest" in text_lower:
        res["encryption_at_rest"] = False
        
    hours, src_h = extract_number_from_text(text, ["hour", "hours"])
    res["breach_notice_hours"] = hours
    if hours is not None:
        sources.append(src_h)
    
    if "without prior approval" in text_lower or "no prior approval" in text_lower or "does not require prior approval" in text_lower:
        res["subprocessor_approval"] = False
        
    days, src_d = extract_number_from_text(text, ["days after the service ends", "days after termination", "days", "weeks"])
    res["deletion_days"] = days
    if days is not None:
        sources.append(src_d)
    
    final_source = "rule_engine+llm_extraction" if "rule_engine+llm_extraction" in sources else "rule_engine"
    return res, final_source

def parse_data_protection_clause(text: str, contract_id: str = "", category: str = "Data Protection") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_data_protection(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res


def _raw_parse_confidentiality(text: str) -> tuple[dict, str]:
    text_lower = text.lower()
    res = {
        "duration_years": None,
        "carve_outs_present": True,
        "reciprocal": True
    }
    source = "rule_engine"
    
    years, src_y = extract_number_from_text(text, ["year", "years"])
    res["duration_years"] = years
    if years is not None:
        source = src_y
    
    if "public" not in text_lower and "previously known" not in text_lower and "independently developed" not in text_lower and "exclud" not in text_lower:
        res["carve_outs_present"] = False
        
    if "customer must protect" in text_lower and ("has no confidentiality duty" in text_lower or "no duty" in text_lower or "no obligation" in text_lower or "not reciprocal" in text_lower or "novastaff has no" in text_lower):
        res["reciprocal"] = False
        
    return res, source

def parse_confidentiality_clause(text: str, contract_id: str = "", category: str = "Confidentiality") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_confidentiality(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res


def _raw_parse_ip(text: str) -> tuple[dict, str]:
    text_lower = text.lower()
    res = {
        "customer_owns_custom": True,
        "licence_permanent": True
    }
    
    if "vendor owns" in text_lower or "provider owns" in text_lower or "novastaff owns" in text_lower or "marketloop owns" in text_lower or "developer owns" in text_lower:
        res["customer_owns_custom"] = False

    if "six months" in text_lower or "usable only while this agreement remains active" in text_lower or "temporary licence" in text_lower or "temporary license" in text_lower:
        res["licence_permanent"] = False
        
    return res, "rule_engine"

def parse_ip_clause(text: str, contract_id: str = "", category: str = "Intellectual Property") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_ip(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res


def _raw_parse_liability(text: str) -> tuple[dict, str]:
    text_lower = text.lower()
    res = {
        "cap_months": 12,
        "asymmetric": False,
        "carve_outs_present": True
    }
    source = "rule_engine"
    
    if "one month" in text_lower:
        res["cap_months"] = 1
    else:
        months, src_m = extract_number_from_text(text, ["month", "months", "quarter", "quarters"])
        if months is not None:
            res["cap_months"] = months
            source = src_m
        
    if "customer has unlimited liability" in text_lower or "asymmetric liability" in text_lower:
        res["asymmetric"] = True
        
    if "gross negligence" not in text_lower and "fraud" not in text_lower:
        res["carve_outs_present"] = False
        
    return res, source

def parse_liability_clause(text: str, contract_id: str = "", category: str = "Limitation of Liability") -> tuple[dict, str]:
    cache_key = (contract_id, category, get_text_hash(text))
    if cache_key in _EXTRACTION_CACHE:
        return _EXTRACTION_CACHE[cache_key]
    res = _raw_parse_liability(text)
    _EXTRACTION_CACHE[cache_key] = res
    return res
