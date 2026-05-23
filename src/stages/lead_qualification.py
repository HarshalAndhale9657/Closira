"""
Stage 2: Lead Qualification

Asks the customer structured questions to qualify them as a lead.
Collects responses, extracts structured data, and produces a
qualification summary once all questions have been answered.
"""

from src.llm_client import send_json_message
from src.models import ConversationState
from src.config import QUALIFICATION_QUESTIONS

# ── System prompt for lead qualification ─────────────────────────────────
LEAD_QUAL_SYSTEM_PROMPT = """You are the AI customer support assistant for {business_name}.
You are now in the LEAD QUALIFICATION stage. Your goal is to ask the customer a few
quick questions to help match them with the right treatment and booking slot.

## INSTRUCTIONS
1. You have a set of qualification questions to ask. Ask them ONE AT A TIME.
2. After the customer responds, extract their answer naturally.
3. Be conversational — don't interrogate. Weave questions into natural dialogue.
4. If the customer provides information voluntarily (e.g., mentions they want Botox),
   count that as an answer to the relevant question.
5. Once all questions are answered, produce a brief qualification summary.

## CURRENT QUESTION TO ASK
{current_question}

## QUESTIONS ALREADY ANSWERED
{answered_questions}

## SOP DATA (for reference)
{sop_context}

## TONE
- Warm, friendly, and efficient
- Make the customer feel heard, not surveyed
- Keep it brief — 1-2 sentences per message

## RESPONSE FORMAT
Respond with a JSON object:
{{
    "response": "Your natural-language message to the customer (asking the question or acknowledging their answer)",
    "extracted_answer": "The customer's answer extracted from their message, or null if they haven't answered yet",
    "question_key": "The key of the question being answered (e.g., 'treatment_interest'), or null",
    "question_complete": true | false
}}
"""

QUALIFICATION_SUMMARY_PROMPT = """You are the AI customer support assistant for {business_name}.
Generate a brief, professional qualification summary based on the customer's responses.

## COLLECTED DATA
{lead_data}

## SOP DATA
{sop_context}

## RESPONSE FORMAT
Respond with a JSON object:
{{
    "summary": "A natural-language qualification summary (2-3 sentences) for the customer",
    "internal_summary": "A structured internal summary for the team",
    "recommended_service": "The most relevant service based on their answers",
    "urgency": "high" | "medium" | "low",
    "next_step": "Recommended next action (e.g., 'Book free consultation')"
}}
"""


def handle_lead_qualification(
    state: ConversationState,
    user_message: str,
    sop_context: str,
    business_name: str,
) -> dict:
    """
    Process lead qualification — ask the next question or extract an answer.

    Returns:
        Dict with keys: response, extracted_answer, question_key, question_complete,
                        and optionally all_complete, qualification_summary
    """
    questions = QUALIFICATION_QUESTIONS
    q_index = state.qualification_question_index

    # Check if all questions have been asked
    if q_index >= len(questions):
        return _generate_summary(state, sop_context, business_name)

    current_q = questions[q_index]

    # Format already-answered questions
    answered = ""
    if state.lead_data:
        answered = "\n".join(
            f"- {k.replace('_', ' ').title()}: {v}"
            for k, v in state.lead_data.items()
        )
    else:
        answered = "None yet."

    system_prompt = LEAD_QUAL_SYSTEM_PROMPT.format(
        business_name=business_name,
        current_question=f"{current_q['question']} (key: {current_q['key']})",
        answered_questions=answered,
        sop_context=sop_context,
    )

    messages = state.get_api_messages()
    if not messages or messages[-1].get("content") != user_message:
        messages.append({"role": "user", "content": user_message})

    result = send_json_message(
        system_prompt=system_prompt,
        messages=messages,
    )

    result.setdefault("response", "")
    result.setdefault("extracted_answer", None)
    result.setdefault("question_key", None)
    result.setdefault("question_complete", False)

    # If the customer answered the current question, store it and advance
    if result.get("question_complete") and result.get("extracted_answer"):
        key = result.get("question_key", current_q["key"])
        state.lead_data[key] = result["extracted_answer"]
        state.qualification_question_index += 1

        # Check if all questions are now done
        if state.qualification_question_index >= len(questions):
            summary_result = _generate_summary(state, sop_context, business_name)
            result["all_complete"] = True
            result["qualification_summary"] = summary_result
            # Append the summary to the response
            if summary_result.get("summary"):
                result["response"] += "\n\n" + summary_result["summary"]

    result["all_complete"] = result.get("all_complete", False)
    return result


def _generate_summary(
    state: ConversationState,
    sop_context: str,
    business_name: str,
) -> dict:
    """Generate the qualification summary from collected lead data."""
    lead_data_str = "\n".join(
        f"- {k.replace('_', ' ').title()}: {v}"
        for k, v in state.lead_data.items()
    )

    system_prompt = QUALIFICATION_SUMMARY_PROMPT.format(
        business_name=business_name,
        lead_data=lead_data_str,
        sop_context=sop_context,
    )

    messages = [{"role": "user", "content": "Please generate the qualification summary."}]

    result = send_json_message(
        system_prompt=system_prompt,
        messages=messages,
    )

    result.setdefault("summary", "Thank you for answering those questions!")
    result.setdefault("internal_summary", "")
    result.setdefault("recommended_service", "Consultation")
    result.setdefault("urgency", "medium")
    result.setdefault("next_step", "Book a free consultation")
    result["all_complete"] = True

    return result
