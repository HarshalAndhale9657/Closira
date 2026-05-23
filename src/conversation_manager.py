"""
Conversation Manager — Orchestrator

Manages the end-to-end conversation flow across all four stages:
1. FAQ Answering
2. Lead Qualification
3. Escalation Detection (runs in parallel on every message)
4. Conversation Summary (generated at session end)

Handles stage transitions, escalation logic, and session lifecycle.
"""

from src.models import ConversationState, ConversationStage, ConversationSummary
from src.sop_loader import load_sop, format_sop_context
from src.stages.faq_answering import handle_faq
from src.stages.lead_qualification import handle_lead_qualification
from src.stages.escalation_detection import check_escalation, process_escalation
from src.stages.conversation_summary import generate_summary


class ConversationManager:
    """
    Orchestrates the customer conversation through all stages.

    Usage:
        manager = ConversationManager()
        greeting = manager.start_session()
        while True:
            response, metadata = manager.process_message(user_input)
            if metadata.get("session_ended"):
                break
    """

    def __init__(self):
        self.state = ConversationState()
        self.sop = load_sop()
        self.sop_context = format_sop_context(self.sop)
        self.business_name = self.sop["business"]["name"]
        self._intent_detected = False  # Has the customer shown purchase interest?
        self._faq_exchange_count = 0

    def start_session(self) -> str:
        """Start a new conversation session and return the greeting message."""
        greeting = (
            f"Hello, welcome to {self.business_name}. "
            f"I'm here to help you with any questions about our services, "
            f"booking, or anything else you'd like to know.\n\n"
            f"How can I help you today?"
        )
        self.state.add_message("assistant", greeting)
        return greeting

    def process_message(self, user_message: str) -> tuple[str, dict]:
        """
        Process a customer message through the appropriate stage.

        Args:
            user_message: The customer's input message.

        Returns:
            Tuple of (response_text, metadata_dict).
            Metadata includes: stage, escalated, sentiment, session_ended, etc.
        """
        user_message = user_message.strip()
        if not user_message:
            return "I didn't catch that — could you say that again?", {"stage": self.state.stage.value}

        # Record the user's message
        self.state.add_message("user", user_message)

        # Check for session-end commands
        if user_message.lower() in ("/summary", "/quit", "quit", "exit", "bye", "goodbye", "end"):
            return self._end_session()

        # Check for status command
        if user_message.lower() == "/status":
            return self._get_status(), {"stage": self.state.stage.value, "is_command": True}

        # Check for manual stage commands
        if user_message.lower() == "/qualify":
            self.state.stage = ConversationStage.LEAD_QUALIFICATION
            return self._handle_lead_qualification_transition(), {
                "stage": self.state.stage.value,
                "stage_changed": True,
            }

        # ── Step 1: Escalation Detection (parallel check on every message) ──
        escalation_result = check_escalation(
            state=self.state,
            user_message=user_message,
            business_name=self.business_name,
        )

        metadata = {
            "stage": self.state.stage.value,
            "sentiment": escalation_result.get("sentiment", "neutral"),
            "escalated": False,
            "session_ended": False,
        }

        # If escalation is triggered, handle it
        if escalation_result.get("should_escalate"):
            handoff_message = process_escalation(
                state=self.state,
                user_message=user_message,
                escalation_result=escalation_result,
            )
            self.state.add_message("assistant", handoff_message)
            metadata["escalated"] = True
            metadata["escalation_reason"] = escalation_result.get("reason", "")
            metadata["escalation_category"] = escalation_result.get("category", "")
            return handoff_message, metadata

        # ── Step 2: Route to the current stage ──
        if self.state.stage == ConversationStage.FAQ:
            return self._handle_faq(user_message, metadata)

        elif self.state.stage == ConversationStage.LEAD_QUALIFICATION:
            return self._handle_lead_qualification(user_message, metadata)

        else:
            return self._handle_faq(user_message, metadata)

    def _handle_faq(self, user_message: str, metadata: dict) -> tuple[str, dict]:
        """Handle the FAQ answering stage."""
        result = handle_faq(
            state=self.state,
            user_message=user_message,
            sop_context=self.sop_context,
            business_name=self.business_name,
        )

        response = result["answer"]
        metadata["confidence"] = result.get("confidence", "medium")
        metadata["source_section"] = result.get("source_section", "unknown")
        metadata["in_sop"] = result.get("in_sop", True)

        # Track SOP gaps
        if not result.get("in_sop", True):
            self.state.record_sop_gap(user_message)
        else:
            self.state.reset_unanswered_count()

        # Track FAQ exchanges and detect purchase intent
        self._faq_exchange_count += 1

        # Auto-transition to lead qualification after some FAQ exchanges
        # if the customer seems interested
        if self._faq_exchange_count >= 2 and result.get("in_sop") and not self._intent_detected:
            if self._detect_intent(user_message):
                self._intent_detected = True
                # Transition to lead qualification
                self.state.stage = ConversationStage.LEAD_QUALIFICATION
                transition_msg = (
                    f"\n\nI'd love to help you take the next step. "
                    f"Let me ask you a couple of quick questions so we can find the "
                    f"right fit for you.\n\n"
                )
                # Get the first qualification question
                qual_result = handle_lead_qualification(
                    state=self.state,
                    user_message="I'm interested",
                    sop_context=self.sop_context,
                    business_name=self.business_name,
                )
                response += transition_msg + qual_result.get("response", "")
                metadata["stage"] = ConversationStage.LEAD_QUALIFICATION.value
                metadata["stage_changed"] = True

        self.state.add_message("assistant", response)
        return response, metadata

    def _handle_lead_qualification(self, user_message: str, metadata: dict) -> tuple[str, dict]:
        """Handle the lead qualification stage."""
        result = handle_lead_qualification(
            state=self.state,
            user_message=user_message,
            sop_context=self.sop_context,
            business_name=self.business_name,
        )

        response = result.get("response", "")
        metadata["question_complete"] = result.get("question_complete", False)
        metadata["all_complete"] = result.get("all_complete", False)

        if result.get("all_complete"):
            metadata["qualification_summary"] = result.get("qualification_summary", {})
            # After qualification, stay ready for more questions or session end
            self.state.stage = ConversationStage.FAQ

        self.state.add_message("assistant", response)
        return response, metadata

    def _handle_lead_qualification_transition(self) -> str:
        """Handle manual transition to lead qualification."""
        result = handle_lead_qualification(
            state=self.state,
            user_message="I'd like to learn more about your services",
            sop_context=self.sop_context,
            business_name=self.business_name,
        )
        response = "Great, let me ask you a few quick questions.\n\n" + result.get("response", "")
        self.state.add_message("assistant", response)
        return response

    def _end_session(self) -> tuple[str, dict]:
        """End the session and generate the conversation summary."""
        summary = generate_summary(
            state=self.state,
            sop_context=self.sop_context,
            business_name=self.business_name,
        )

        farewell = (
            "Thank you for chatting with us! Here's a summary of our conversation:\n\n"
        )

        self.state.add_message("assistant", farewell)

        return farewell, {
            "stage": "conversation_summary",
            "session_ended": True,
            "summary": summary.to_dict(),
        }

    def _get_status(self) -> str:
        """Get a status string for the current conversation state."""
        lines = [
            f"Conversation Status",
            f"  Stage:        {self.state.stage.value}",
            f"  Messages:     {len(self.state.messages)}",
            f"  Lead Data:    {len(self.state.lead_data)} fields collected",
            f"  SOP Gaps:     {len(self.state.sop_gaps)}",
            f"  Escalations:  {len(self.state.escalation_events)}",
            f"  Escalated:    {'Yes' if self.state.is_escalated else 'No'}",
        ]
        return "\n".join(lines)

    def _detect_intent(self, message: str) -> bool:
        """
        Simple heuristic to detect purchase/booking intent from the customer.
        Used to trigger the transition from FAQ to Lead Qualification.
        """
        intent_keywords = [
            "book", "appointment", "schedule", "interested",
            "want", "like to", "how much", "price", "cost",
            "sign up", "get started", "try", "consultation",
            "available", "when can", "next step",
        ]
        message_lower = message.lower()
        return any(kw in message_lower for kw in intent_keywords)
