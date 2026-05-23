"""
Stage 3: Escalation Detection

Runs as a parallel classifier on every customer message to detect
when the AI should hand off to a human agent. Detects complaints,
medical questions, pricing negotiation, explicit requests, and more.
"""

import json
from datetime import datetime
from pathlib import Path

from src.llm_client import send_json_message
from src.models import ConversationState, EscalationEvent
from src.config import ESCALATION_LOG_PATH, MAX_UNANSWERED_BEFORE_ESCALATION

# ── System prompt for escalation detection ───────────────────────────────
ESCALATION_SYSTEM_PROMPT = """You are an escalation detection classifier for {business_name}'s
customer support AI. Your job is to analyze the customer's latest message and determine
whether the conversation should be escalated to a human agent.

## ESCALATION TRIGGERS — Escalate if ANY of these are detected:
1. **Complaint / Dissatisfaction**: Customer expresses frustration, anger, or dissatisfaction
2. **Medical question**: Customer asks about safety, side effects, contraindications, allergies,
   or any question requiring clinical/medical judgment
3. **Pricing negotiation**: Customer tries to negotiate prices, asks for discounts, or pushes
   back on costs
4. **Explicit request**: Customer explicitly asks to speak to a human, manager, supervisor, or
   "real person"
5. **Adverse reaction**: Customer mentions bad reactions, complications, or emergency situations
6. **Low confidence**: The question is ambiguous or complex enough that the AI is likely to
   give an unreliable answer

## IMPORTANT
- Be sensitive to subtle expressions of frustration (e.g., "this is getting ridiculous",
  "I've been waiting", "nobody is helping me")
- Medical questions include anything about individual health conditions, medication interactions,
  pregnancy, or whether a treatment is "safe for me"
- Pricing negotiation includes "can you do it cheaper", "that's too expensive", "any discounts"

## CUSTOMER'S LATEST MESSAGE
"{customer_message}"

## CONVERSATION CONTEXT
{conversation_context}

## RESPONSE FORMAT
Respond with a JSON object:
{{
    "should_escalate": true | false,
    "reason": "Brief explanation of why escalation is or isn't needed",
    "category": "complaint" | "medical_question" | "pricing_negotiation" | "explicit_human_request" | "adverse_reaction" | "low_confidence" | "none",
    "sentiment": "positive" | "neutral" | "negative" | "angry",
    "confidence": "high" | "medium" | "low"
}}
"""

ESCALATION_HANDOFF_MESSAGE = (
    "I understand this is important to you, and I want to make sure you get the best "
    "help possible. Let me connect you with a member of our team who can assist you "
    "further. A team member will be with you shortly."
)


def check_escalation(
    state: ConversationState,
    user_message: str,
    business_name: str,
) -> dict:
    """
    Check whether the customer's message triggers an escalation.

    This runs on EVERY customer message as a parallel safety check.

    Args:
        state: Current conversation state.
        user_message: The customer's latest message.
        business_name: Name of the business.

    Returns:
        Dict with keys: should_escalate, reason, category, sentiment, confidence
    """
    # Build conversation context (last 6 messages for efficiency)
    recent_messages = state.messages[-6:] if len(state.messages) > 6 else state.messages
    context = "\n".join(
        f"{'Customer' if m.role == 'user' else 'AI'}: {m.content}"
        for m in recent_messages
    )

    system_prompt = ESCALATION_SYSTEM_PROMPT.format(
        business_name=business_name,
        customer_message=user_message,
        conversation_context=context if context else "No prior context.",
    )

    messages = [{"role": "user", "content": f"Analyze this message for escalation: \"{user_message}\""}]

    result = send_json_message(
        system_prompt=system_prompt,
        messages=messages,
        temperature=0.1,  # Very low for classification
    )

    result.setdefault("should_escalate", False)
    result.setdefault("reason", "")
    result.setdefault("category", "none")
    result.setdefault("sentiment", "neutral")
    result.setdefault("confidence", "medium")

    # Also check consecutive unanswered count
    if state.unanswered_count >= MAX_UNANSWERED_BEFORE_ESCALATION and not result["should_escalate"]:
        result["should_escalate"] = True
        result["reason"] = f"More than {MAX_UNANSWERED_BEFORE_ESCALATION} consecutive questions could not be answered from the SOP."
        result["category"] = "unanswered_sop_gap"

    return result


def process_escalation(
    state: ConversationState,
    user_message: str,
    escalation_result: dict,
) -> str:
    """
    Process an escalation: log the event and return the handoff message.

    Args:
        state: Current conversation state.
        user_message: The message that triggered escalation.
        escalation_result: Result from check_escalation().

    Returns:
        The handoff message to send to the customer.
    """
    # Create and record the escalation event
    event = EscalationEvent(
        reason=escalation_result.get("reason", "Escalation triggered"),
        category=escalation_result.get("category", "unknown"),
        trigger_message=user_message,
        sentiment=escalation_result.get("sentiment", "neutral"),
    )
    state.record_escalation(event)

    # Log to file
    _log_escalation(event)

    return ESCALATION_HANDOFF_MESSAGE


def _log_escalation(event: EscalationEvent) -> None:
    """Append escalation event to the log file."""
    log_path = ESCALATION_LOG_PATH
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing log
    existing = []
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing = []

    existing.append(event.to_dict())

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
