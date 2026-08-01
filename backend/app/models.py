from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

from typing import Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

class ClauseCategory(str):
    @property
    def value(self) -> str:
        return str(self)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(cls, core_schema.str_schema())


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
    rule_engine_llm_extraction = "rule_engine+llm_extraction"

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

class ContractCreate(BaseModel):
    title: str
    parties: str
    raw_text: str

class StandardCreate(BaseModel):
    id: str
    category: str
    text: str
