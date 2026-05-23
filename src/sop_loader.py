"""
SOP (Standard Operating Procedure) data loader.

Loads the SOP JSON file and provides methods to retrieve the full SOP
context as a formatted string for injection into the system prompt.
"""

import json
from pathlib import Path
from src.config import SOP_DATA_PATH


def load_sop(path: Path | None = None) -> dict:
    """Load SOP data from JSON file."""
    sop_path = path or SOP_DATA_PATH
    if not sop_path.exists():
        raise FileNotFoundError(
            f"SOP data file not found at {sop_path}. "
            "Please ensure sop_data.json is in the project root."
        )
    with open(sop_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_sop_context(sop: dict) -> str:
    """
    Format the full SOP data into a readable string for the system prompt.

    This string is injected directly into the LLM's system prompt so the
    model has complete access to all business information.
    """
    lines = []

    # Business info
    biz = sop["business"]
    lines.append(f"=== BUSINESS INFORMATION ===")
    lines.append(f"Name: {biz['name']}")
    lines.append(f"Type: {biz['type']}")
    lines.append(f"Location: {biz.get('location', 'N/A')}")
    lines.append(f"Phone: {biz.get('phone', 'N/A')}")
    lines.append(f"Email: {biz.get('email', 'N/A')}")
    lines.append(f"Website: {biz.get('website', 'N/A')}")
    lines.append("")

    # Hours
    lines.append(f"=== OPENING HOURS ===")
    for day, hours in sop["hours"].items():
        lines.append(f"  {day.capitalize()}: {hours}")
    lines.append("")

    # Services
    lines.append(f"=== SERVICES & PRICING ===")
    for svc in sop["services"]:
        price_str = svc.get("starting_price", svc.get("price", "N/A"))
        lines.append(f"  Service: {svc['name']}")
        lines.append(f"    Price: {price_str}")
        lines.append(f"    Description: {svc['description']}")
        if "duration" in svc:
            lines.append(f"    Duration: {svc['duration']}")
        if "results_timeline" in svc:
            lines.append(f"    Results: {svc['results_timeline']}")
        if "longevity" in svc:
            lines.append(f"    Longevity: {svc['longevity']}")
        if "downtime" in svc:
            lines.append(f"    Downtime: {svc['downtime']}")
        if "note" in svc:
            lines.append(f"    Note: {svc['note']}")
        lines.append("")

    # Booking
    lines.append(f"=== BOOKING INFORMATION ===")
    booking = sop["booking"]
    lines.append(f"  Booking Methods: {', '.join(booking['methods'])}")
    lines.append(f"  Cancellation Policy: {booking['cancellation_policy']}")
    lines.append(f"  Deposit: {booking['deposit']}")
    if "waiting_list" in booking:
        lines.append(f"  Waiting List: {booking['waiting_list']}")
    lines.append("")

    # Policies
    if "policies" in sop:
        lines.append(f"=== POLICIES ===")
        for key, value in sop["policies"].items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")
        lines.append("")

    # FAQs
    lines.append(f"=== FREQUENTLY ASKED QUESTIONS ===")
    for faq in sop.get("faqs", []):
        lines.append(f"  Q: {faq['question']}")
        lines.append(f"  A: {faq['answer']}")
        lines.append("")

    # Escalation rules
    lines.append(f"=== ESCALATION RULES ===")
    esc = sop.get("escalation_rules", {})
    if isinstance(esc, dict):
        lines.append("  Escalate to a human agent when:")
        for trigger in esc.get("triggers", []):
            lines.append(f"    - {trigger}")
        lines.append(f"  Escalation Response: {esc.get('escalation_response', '')}")
    elif isinstance(esc, list):
        lines.append("  Escalate to a human agent when:")
        for trigger in esc:
            lines.append(f"    - {trigger}")
    lines.append("")

    return "\n".join(lines)


def get_sop_context(path: Path | None = None) -> str:
    """Load SOP and return formatted context string."""
    sop = load_sop(path)
    return format_sop_context(sop)
