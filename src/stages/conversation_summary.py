"""
Stage 4: Conversation Summary

Generates a structured end-of-session summary capturing customer intent,
key details collected, SOP gaps identified, escalation events, and
recommended next actions.
"""

from src.llm_client import send_json_message
from src.models import ConversationState, ConversationSummary

# ── System prompt for conversation summary ───────────────────────────────
SUMMARY_SYSTEM_PROMPT = """You are a conversation analysis assistant for {business_name}.
Analyze the complete conversation transcript below and produce a structured summary.

## FULL CONVERSATION TRANSCRIPT
{transcript}

## LEAD QUALIFICATION DATA COLLECTED
{lead_data}

## SOP GAPS IDENTIFIED DURING CONVERSATION
{sop_gaps}

## ESCALATION EVENTS
{escalation_events}

## INSTRUCTIONS
Produce a comprehensive, accurate summary. Do not invent details not present in the
conversation. Be specific about what the customer asked and what was discussed.

## RESPONSE FORMAT
Respond with a JSON object:
{{
    "customer_intent": "A clear 1-2 sentence summary of what the customer wanted",
    "key_details": {{
        "treatment_interest": "What treatment(s) the customer asked about, or 'Not specified'",
        "experience_level": "First-time or returning, or 'Not discussed'",
        "preferred_timing": "When they want to book, or 'Not discussed'",
        "budget_mentioned": true | false,
        "contact_info_provided": true | false,
        "additional_notes": "Any other relevant details"
    }},
    "sop_gaps": ["List of questions the SOP could not answer"],
    "escalation_events": ["List of escalation reasons, if any"],
    "customer_sentiment": "Overall sentiment: positive, neutral, negative, or mixed",
    "recommended_next_action": "Specific recommended next step for the team"
}}
"""


def generate_summary(
    state: ConversationState,
    sop_context: str,
    business_name: str,
) -> ConversationSummary:
    """
    Generate a structured conversation summary from the full session.

    Args:
        state: Complete conversation state with all history.
        sop_context: The SOP context string (for reference).
        business_name: Name of the business.

    Returns:
        ConversationSummary object with all fields populated.
    """
    # Format the full transcript
    transcript = "\n".join(
        f"{'Customer' if m.role == 'user' else 'AI'}: {m.content}"
        for m in state.messages
        if m.role in ("user", "assistant")
    )

    if not transcript:
        transcript = "No messages exchanged."

    # Format lead data
    lead_data = "None collected."
    if state.lead_data:
        lead_data = "\n".join(
            f"- {k.replace('_', ' ').title()}: {v}"
            for k, v in state.lead_data.items()
        )

    # Format SOP gaps
    sop_gaps = "None identified."
    if state.sop_gaps:
        sop_gaps = "\n".join(f"- {gap}" for gap in state.sop_gaps)

    # Format escalation events
    escalation_events = "None."
    if state.escalation_events:
        escalation_events = "\n".join(
            f"- [{e.category}] {e.reason} (triggered by: \"{e.trigger_message[:80]}\")"
            for e in state.escalation_events
        )

    system_prompt = SUMMARY_SYSTEM_PROMPT.format(
        business_name=business_name,
        transcript=transcript,
        lead_data=lead_data,
        sop_gaps=sop_gaps,
        escalation_events=escalation_events,
    )

    messages = [{"role": "user", "content": "Generate the conversation summary now."}]

    result = send_json_message(
        system_prompt=system_prompt,
        messages=messages,
    )

    # Build the ConversationSummary
    summary = ConversationSummary(
        customer_intent=result.get("customer_intent", "Not determined"),
        key_details=result.get("key_details", {}),
        sop_gaps=result.get("sop_gaps", state.sop_gaps),
        escalation_events=[
            e.to_dict() for e in state.escalation_events
        ] if state.escalation_events else [],
        recommended_next_action=result.get("recommended_next_action", "Follow up with customer"),
    )

    state.summary = summary
    return summary
