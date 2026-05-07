from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ExtractedFields(BaseModel):
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
    property_address: Optional[str] = None
    property_value: Optional[float] = Field(None, description="Numeric value, in AED or local currency")
    deposit_percentage: Optional[float] = None
    balance_percentage: Optional[float] = None
    due_date: Optional[str] = Field(None, description="ISO 8601 (YYYY-MM-DD) or human-readable")
    jurisdiction: Optional[str] = None
    effective_date: Optional[str] = Field(None, description="ISO 8601 (YYYY-MM-DD) preferred")
    additional_clauses: Optional[list[str]] = Field(
        default=None,
        description="Additional parties or notable clauses found in the deed",
    )


Severity = Literal["INFO", "WARNING", "CRITICAL"]


class Rule(BaseModel):
    rule_id: str = Field(description="Unique string e.g. RULE_001")
    rule_name: str
    source_clause: str = Field(description="Verbatim or paraphrased clause from the deed")
    condition: str = Field(description="Programmatic condition string e.g. payment_status == LATE")
    action: str = Field(description="Function or action name e.g. calculate_fee")
    params: dict[str, Any] = Field(default_factory=dict)
    blockchain_event: Optional[str] = Field(None, description="EVM event name e.g. TriggerPenaltyProvision")
    severity: Severity = "INFO"
    tags: list[str] = Field(default_factory=list)


class RulesResponse(BaseModel):
    """Wrapper for the rule-generation agent's structured output."""

    rules: list[Rule]


class Deed(BaseModel):
    id: int
    file_hash: str
    raw_text: str
    extracted_fields: ExtractedFields
    rules: list[Rule]
    model_version: str
    created_at: str


class ExtractResponse(BaseModel):
    deed_id: int
    file_hash: str
    raw_text: str
    extracted_fields: ExtractedFields
    rules: list[Rule]
    cached: bool = False
