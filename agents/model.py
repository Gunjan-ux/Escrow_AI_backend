import logging

from config import (
    AGENT_USE_BEDROCK,
    ANTHROPIC_MODEL_ID,
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    AWS_SESSION_TOKEN,
    BEDROCK_MAX_TOKENS,
    BEDROCK_MODEL_ID,
    BEDROCK_TEMPERATURE,
)

logger = logging.getLogger(__name__)


def build_model():
    """Return the Agno model wrapper for the active backend (Bedrock or direct Anthropic)."""
    if AGENT_USE_BEDROCK:
        from agno.models.aws import Claude as BedrockClaude

        logger.info(
            "[model] Using AWS Bedrock Claude (id=%s region=%s temp=%s max_tokens=%s).",
            BEDROCK_MODEL_ID,
            AWS_REGION,
            BEDROCK_TEMPERATURE,
            BEDROCK_MAX_TOKENS,
        )
        return BedrockClaude(
            id=BEDROCK_MODEL_ID,
            temperature=BEDROCK_TEMPERATURE,
            max_tokens=BEDROCK_MAX_TOKENS,
            aws_access_key=AWS_ACCESS_KEY_ID,
            aws_secret_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN,
            aws_region=AWS_REGION,
        )

    from agno.models.anthropic import Claude as AnthropicClaude

    logger.info("[model] Using direct Anthropic Claude (id=%s).", ANTHROPIC_MODEL_ID)
    return AnthropicClaude(id=ANTHROPIC_MODEL_ID, temperature=0)
