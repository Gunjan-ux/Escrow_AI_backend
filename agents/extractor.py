import logging
from functools import lru_cache

from agno.agent import Agent

from agents.model import build_model
from config import AGENT_USE_BEDROCK, PROMPTS_DIR
from schemas import ExtractedFields

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    return (PROMPTS_DIR / "extractor_system.txt").read_text()


@lru_cache(maxsize=1)
def _agent() -> Agent:
    logger.info("[extractor] Initializing extraction agent.")
    kwargs = dict(
        model=build_model(),
        description=_system_prompt(),
        use_json_mode=True,
    )
    if not AGENT_USE_BEDROCK:
        kwargs["output_schema"] = ExtractedFields
    return Agent(**kwargs)


def extract_fields(raw_text: str) -> ExtractedFields:
    """Run the extraction agent on raw OCR text and return structured fields."""
    logger.info("[extractor] Extracting fields (chars=%d).", len(raw_text))
    response = _agent().run(raw_text)
    content = response.content
    if isinstance(content, ExtractedFields):
        return content
    if isinstance(content, str):
        return ExtractedFields.model_validate_json(content)
    return ExtractedFields.model_validate(content)
