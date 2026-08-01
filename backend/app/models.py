from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ClauseCategory(str, Enum):
    Payment = "Payment"
    Termination = "Termination"
    DataProtection = "Data Protection"
    Confidentiality = "Confidentiality"
    AutomaticRenewal = "Automatic Renewal"
    IntellectualProperty = "Intellectual Property"
    LimitationOfLiability = "Limitation of Liability"

class RiskLevel(str, Enum):
    LowRisk = "Low Risk"
    MediumRisk = "Medium Risk"
    HighRisk = "High Risk"
    NotEnoughInformation = "Not Enough Information"

class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    marked_for_review = "marked_for_review"

class ReviewSource(str, Enum):
    rule_engine = "rule_engine"
    rule_engine_llm = "rule_engine+llm"

class ContractSummary(BaseModel):
    id: str
    title: str
    parties: str

class ContractDetail(ContractSummary):
    raw_text: str
    dataset_note: Optional[str] = None

class Clause(BaseModel):
    category: ClauseCategory
    present: bool
    heading: Optional[str] = None
    text: Optional[str] = None

class Standard(BaseModel):
    id: str
    category: ClauseCategory
    text: str

class ReviewRequest(BaseModel):
    contract_id: str
    category: ClauseCategory

class ReviewResult(BaseModel):
    review_id: int
    contract_id: str
    category: ClauseCategory
    risk_level: RiskLevel
    reason: str
    contract_evidence: Optional[str] = None
    standard_id: Optional[str] = None
    standard_text: Optional[str] = None
    source: ReviewSource
    status: ReviewStatus
    reviewer_note: Optional[str] = None
    human_review: str = "Required"

class ReviewDecisionRequest(BaseModel):
    status: ReviewStatus
    reviewer_note: Optional[str] = None

class ErrorModel(BaseModel):
    error: bool = True
    code: str
    message: str
