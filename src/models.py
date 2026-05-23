"""
Data models for Closira AI Customer Support Workflow.

Defines the core data structures for managing conversation state,
messages, escalation events, and conversation summaries.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConversationStage(Enum):
    """The current stage of the customer conversation."""
    FAQ = "faq_answering"
    LEAD_QUALIFICATION = "lead_qualification"
    SUMMARY = "conversation_summary"


class EscalationCategory(Enum):
    """Categories of escalation triggers."""
    COMPLAINT = "complaint"
    MEDICAL = "medical_question"
    PRICING = "pricing_negotiation"
    SOP_GAP = "unanswered_sop_gap"
    EXPLICIT_REQUEST = "explicit_human_request"
    LOW_CONFIDENCE = "low_confidence"
    ADVERSE_REACTION = "adverse_reaction"


class Sentiment(Enum):
    """Detected customer sentiment."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"


@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user", "assistant", or "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_api_format(self) -> dict:
        """Convert to OpenAI API message format."""
        return {"role": self.role, "content": self.content}


@dataclass
class EscalationEvent:
    """A logged escalation event."""
    reason: str
    category: str
    trigger_message: str
    sentiment: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "reason": self.reason,
            "category": self.category,
            "trigger_message": self.trigger_message,
            "sentiment": self.sentiment,
            "timestamp": self.timestamp,
        }


@dataclass
class ConversationSummary:
    """Structured summary generated at the end of a conversation."""
    customer_intent: str = ""
    key_details: dict[str, Any] = field(default_factory=dict)
    sop_gaps: list[str] = field(default_factory=list)
    escalation_events: list[dict] = field(default_factory=list)
    recommended_next_action: str = ""

    def to_dict(self) -> dict:
        return {
            "customer_intent": self.customer_intent,
            "key_details": self.key_details,
            "sop_gaps": self.sop_gaps,
            "escalation_events": self.escalation_events,
            "recommended_next_action": self.recommended_next_action,
        }


@dataclass
class ConversationState:
    """
    Holds the full state of an ongoing customer conversation.

    Tracks the current stage, message history, lead qualification data,
    escalation events, and identified SOP gaps.
    """
    stage: ConversationStage = ConversationStage.FAQ
    messages: list[Message] = field(default_factory=list)
    lead_data: dict[str, str] = field(default_factory=dict)
    qualification_question_index: int = 0
    escalation_events: list[EscalationEvent] = field(default_factory=list)
    is_escalated: bool = False
    sop_gaps: list[str] = field(default_factory=list)
    unanswered_count: int = 0
    summary: ConversationSummary | None = None

    def add_message(self, role: str, content: str) -> Message:
        """Add a message to the conversation history."""
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        return msg

    def get_api_messages(self) -> list[dict]:
        """Get all messages in OpenAI API format (excluding system messages)."""
        return [
            msg.to_api_format()
            for msg in self.messages
            if msg.role in ("user", "assistant")
        ]

    def record_escalation(self, event: EscalationEvent) -> None:
        """Record an escalation event and mark conversation as escalated."""
        self.escalation_events.append(event)
        self.is_escalated = True

    def record_sop_gap(self, question: str) -> None:
        """Record a question the SOP couldn't answer."""
        if question not in self.sop_gaps:
            self.sop_gaps.append(question)
        self.unanswered_count += 1

    def reset_unanswered_count(self) -> None:
        """Reset the consecutive unanswered question counter."""
        self.unanswered_count = 0
