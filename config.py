import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = ROOT_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
PROMPTS_DIR = ROOT_DIR / "prompts"
DB_PATH = ROOT_DIR / os.getenv("DB_PATH", "data/escrow.db")

AGENT_USE_BEDROCK = os.getenv("AGENT_USE_BEDROCK", "false").lower() in {"1", "true", "yes"}

# AWS Bedrock
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN") or None

BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
BEDROCK_TEMPERATURE = float(os.getenv("BEDROCK_TEMPERATURE", "0"))
BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "8192"))

# Direct Anthropic API (used when AGENT_USE_BEDROCK is false)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_ID = os.getenv("MODEL_ID", "claude-sonnet-4-6")

# The model id we record on saved deeds (for traceability)
ACTIVE_MODEL_ID = BEDROCK_MODEL_ID if AGENT_USE_BEDROCK else ANTHROPIC_MODEL_ID

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
