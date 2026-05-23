"""
Configuration module for Closira AI Customer Support Workflow.

Loads environment variables and defines application-wide settings
including model parameters, escalation thresholds, and file paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────────────────
load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
SOP_DATA_PATH = PROJECT_ROOT / "sop_data.json"
ESCALATION_LOG_PATH = PROJECT_ROOT / "logs" / "escalation_log.json"

# ── OpenAI Configuration ─────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# Low temperature for reliability — we want grounded, predictable responses
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# ── Escalation Thresholds ────────────────────────────────────────────────
# Number of consecutive unanswered (out-of-SOP) questions before auto-escalation
MAX_UNANSWERED_BEFORE_ESCALATION = 2

# ── Lead Qualification Settings ──────────────────────────────────────────
QUALIFICATION_QUESTIONS = [
    {
        "key": "treatment_interest",
        "question": "Which treatment are you most interested in? For example, Botox, fillers, or would you like a general consultation?",
    },
    {
        "key": "experience_level",
        "question": "Have you had this type of treatment before, or would this be your first time?",
    },
    {
        "key": "preferred_timing",
        "question": "When would you ideally like to come in? Do you have a preferred day or time?",
    },
]

# ── Validation ────────────────────────────────────────────────────────────
def validate_config():
    """Validate that all required configuration is present."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Please set it in your .env file or as an environment variable.\n"
            "See .env.example for the expected format."
        )
