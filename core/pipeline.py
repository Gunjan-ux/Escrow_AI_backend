import logging

from agents.extractor import extract_fields
from agents.rule_generator import generate_rules
from schemas import ExtractedFields, Rule

logger = logging.getLogger(__name__)


def analyze_deed(raw_text: str) -> tuple[ExtractedFields, list[Rule]]:
    """Two-agent pipeline: extract fields, then generate rules using those fields."""
    logger.info("[pipeline] Stage 1: extracting fields.")
    fields = extract_fields(raw_text)
    logger.info("[pipeline] Stage 2: generating rules.")
    rules = generate_rules(fields, raw_text)
    logger.info("[pipeline] Done. fields=%s rules=%d", _summary(fields), len(rules))
    return fields, rules


def _summary(fields: ExtractedFields) -> str:
    return f"buyer={fields.buyer_name!r} seller={fields.seller_name!r} value={fields.property_value}"
