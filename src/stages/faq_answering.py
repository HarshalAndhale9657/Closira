"""
Stage 1: FAQ Answering

Handles inbound customer questions by answering strictly from the SOP data.
Uses structured JSON output to track confidence, source sections, and
whether the answer is within the SOP boundaries.
"""

from src.llm_client import send_json_message
from src.models import ConversationState

# ── System prompt for FAQ answering ──────────────────────────────────────
FAQ_SYSTEM_PROMPT = """You are the AI customer support assistant for {business_name}.
Your role is to answer customer questions warmly, professionally, and accurately.

## CRITICAL RULES — READ CAREFULLY

1. **ONLY answer from the SOP data provided below.** Do NOT invent, assume, guess, or
   infer ANY information that is not explicitly stated in the SOP.
2. If the customer asks something NOT covered in the SOP, you MUST say you don't have
   that information and offer to connect them with a team member. NEVER make up an answer.
3. Always cite which section of the SOP your answer comes from (services, booking, policies, etc.).
4. If you are uncertain whether the SOP covers the question, err on the side of caution:
   say "I don't have that specific information in our records" and offer escalation.

## TONE & PERSONA
- Warm, professional, and reassuring
- Conversational but polished — avoid overly clinical or casual language
- Acknowledge the customer's concerns before answering
- Keep responses concise and scannable (customers message on mobile)
- End with a clear next step (e.g., booking a consultation)

## SOP DATA
{sop_context}

## RESPONSE FORMAT
You MUST respond with a JSON object in this exact format:
{{
    "answer": "Your natural-language response to the customer",
    "confidence": "high" | "medium" | "low",
    "source_section": "The SOP section this answer comes from (e.g., 'services', 'booking', 'policies')",
    "in_sop": true | false
}}

- Set "in_sop" to false if the question is not covered by the SOP data.
- Set "confidence" to "low" if you are unsure about the answer.
- The "answer" field should be the actual customer-facing response (warm, helpful tone).
"""


def handle_faq(
    state: ConversationState,
    user_message: str,
    sop_context: str,
    business_name: str,
) -> dict:
    """
    Process a customer FAQ question against the SOP data.

    Args:
        state: Current conversation state.
        user_message: The customer's message.
        sop_context: Formatted SOP data string.
        business_name: Name of the business.

    Returns:
        Dict with keys: answer, confidence, source_section, in_sop
    """
    system_prompt = FAQ_SYSTEM_PROMPT.format(
        business_name=business_name,
        sop_context=sop_context,
    )

    # Build message history for context
    messages = state.get_api_messages()

    # Ensure the current message is included
    if not messages or messages[-1].get("content") != user_message:
        messages.append({"role": "user", "content": user_message})

    result = send_json_message(
        system_prompt=system_prompt,
        messages=messages,
    )

    # Ensure all expected keys are present
    result.setdefault("answer", "I'm sorry, I couldn't process that. Could you rephrase your question?")
    result.setdefault("confidence", "medium")
    result.setdefault("source_section", "unknown")
    result.setdefault("in_sop", True)

    return result
