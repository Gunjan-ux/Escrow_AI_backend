import logging
from functools import lru_cache

from agno.agent import Agent

from agents.model import build_model
from config import PROMPTS_DIR
from schemas import ExtractedFields, Rule, RulesResponse

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    return (PROMPTS_DIR / "rule_generator_system.txt").read_text()


@lru_cache(maxsize=1)
def _agent() -> Agent:
    logger.info("[rule_generator] Initializing rule-generation agent.")
    return Agent(
        model=build_model(),
        description=_system_prompt(),
        output_schema=RulesResponse,
        use_json_mode=True,
    )


def _build_user_message(fields: ExtractedFields, raw_text: str) -> str:
    fields_json = fields.model_dump_json(indent=2)
    return (
        "EXTRACTED FIELDS:\n"
        f"{fields_json}\n\n"
        "DEED TEXT:\n"
        f"{raw_text}"
    )


def generate_rules(fields: ExtractedFields, raw_text: str) -> list[Rule]:
    """Run the rule-generation agent and return a list of structured rules."""
    logger.info("[rule_generator] Generating rules (chars=%d).", len(raw_text))
    response = _agent().run(_build_user_message(fields, raw_text))
    content = response.content
    if isinstance(content, RulesResponse):
        return content.rules
    if isinstance(content, str):
        return RulesResponse.model_validate_json(content).rules
    return RulesResponse.model_validate(content).rules
