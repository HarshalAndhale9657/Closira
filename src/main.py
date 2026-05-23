"""
Closira AI Customer Support Workflow — CLI Entry Point

Interactive command-line interface for simulating customer conversations
with the AI-powered support workflow.

Usage:
    python -m src.main
    python src/main.py

Commands:
    /summary  — End session and generate summary
    /status   — Show current conversation status
    /qualify  — Manually switch to lead qualification stage
    /quit     — End the session
    bye/exit  — End the session
"""

import sys
import signal
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.rule import Rule
from rich import box

from src.config import validate_config
from src.conversation_manager import ConversationManager
from src.llm_client import get_token_usage

# ── Console setup ────────────────────────────────────────────────────────
console = Console()

# ── Theme ────────────────────────────────────────────────────────────────
ACCENT = "bright_cyan"
ACCENT_DIM = "cyan"
USER_COLOR = "bright_green"
WARN_COLOR = "bright_yellow"
ERROR_COLOR = "bright_red"
MUTED = "grey62"

STAGE_LABELS = {
    "faq_answering": ("FAQ", "bright_cyan"),
    "lead_qualification": ("QUALIFY", "bright_magenta"),
    "conversation_summary": ("SUMMARY", "bright_yellow"),
}


def print_header():
    """Print a clean, minimal application header."""
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    title = Text()
    title.append("CLOSIRA", style=f"bold {ACCENT}")
    title.append("  AI Customer Support", style="bold white")

    console.print()
    console.print(Panel(
        title,
        border_style=ACCENT_DIM,
        box=box.HEAVY,
        padding=(1, 3),
        subtitle=f"[{MUTED}]{now}[/{MUTED}]",
        subtitle_align="right",
    ))

    # Command hints — compact bar
    hints = Text()
    hints.append("  Commands: ", style=MUTED)
    for cmd, desc in [("/quit", "end"), ("/status", "info"), ("/qualify", "qualify"), ("/summary", "summarise")]:
        hints.append(cmd, style=f"bold {ACCENT}")
        hints.append(f" {desc}  ", style=MUTED)
    console.print(hints)
    console.print()


def _stage_tag(stage: str) -> Text:
    """Build a compact stage tag like [FAQ] or [QUALIFY]."""
    label, color = STAGE_LABELS.get(stage, ("AI", ACCENT))
    tag = Text()
    tag.append(f" {label} ", style=f"bold white on {color}")
    return tag


def print_ai_response(response: str, metadata: dict):
    """Print the AI's response with clean professional formatting."""
    stage = metadata.get("stage", "unknown")

    # ── Escalation alert ──
    if metadata.get("escalated"):
        console.print()
        reason = metadata.get("escalation_reason", "N/A")
        category = metadata.get("escalation_category", "N/A").replace("_", " ").upper()

        alert_content = Text()
        alert_content.append("ESCALATION", style=f"bold {ERROR_COLOR}")
        alert_content.append(f"  [{category}]\n\n", style=f"bold {WARN_COLOR}")
        alert_content.append("Reason: ", style="bold")
        alert_content.append(reason)

        console.print(Panel(
            alert_content,
            border_style=ERROR_COLOR,
            box=box.HEAVY,
            padding=(0, 2),
        ))

    # ── Stage transition notice ──
    if metadata.get("stage_changed"):
        label, color = STAGE_LABELS.get(stage, ("AI", ACCENT))
        console.print(f"  [{MUTED}]--- Switched to {label} stage ---[/{MUTED}]")

    # ── AI response panel ──
    console.print()
    tag = _stage_tag(stage)

    console.print(Panel(
        response,
        border_style=ACCENT_DIM,
        box=box.ROUNDED,
        title=tag,
        title_align="left",
        padding=(1, 3),
    ))

    # ── Confidence footer (FAQ stage only) ──
    if metadata.get("confidence") and stage == "faq_answering":
        confidence = metadata["confidence"]
        in_sop = metadata.get("in_sop", True)
        source = metadata.get("source_section", "—")

        conf_styles = {"high": "green", "medium": "yellow", "low": "red"}
        conf_color = conf_styles.get(confidence, "white")
        sop_label = "SOP" if in_sop else "NOT IN SOP"
        sop_color = "green" if in_sop else WARN_COLOR

        footer = Text("  ")
        footer.append(f" {sop_label} ", style=f"bold white on {sop_color}")
        footer.append(f"  confidence: ", style=MUTED)
        footer.append(confidence, style=f"bold {conf_color}")
        footer.append(f"  source: ", style=MUTED)
        footer.append(source, style="white")
        console.print(footer)


def print_summary(summary: dict):
    """Print the conversation summary with structured professional layout."""
    console.print()
    console.print(Rule(f"[bold {ACCENT}]Conversation Summary[/bold {ACCENT}]", style=ACCENT_DIM))
    console.print()

    # ── Customer intent ──
    intent = summary.get("customer_intent", "N/A")
    console.print(f"  [bold]Intent:[/bold]  {intent}")
    console.print()

    # ── Key details table ──
    key_details = summary.get("key_details", {})
    if key_details:
        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style=ACCENT_DIM,
            show_header=True,
            header_style=f"bold {ACCENT}",
            padding=(0, 2),
            expand=False,
        )
        table.add_column("Detail", style="bold", min_width=22)
        table.add_column("Value", min_width=30)

        for key, value in key_details.items():
            display_key = key.replace("_", " ").title()
            if isinstance(value, bool):
                display_value = "Yes" if value else "No"
            else:
                display_value = str(value)
            table.add_row(display_key, display_value)

        console.print(table)
        console.print()

    # ── SOP Gaps ──
    sop_gaps = summary.get("sop_gaps", [])
    if sop_gaps:
        console.print(f"  [bold {WARN_COLOR}]SOP Gaps:[/bold {WARN_COLOR}]")
        for gap in sop_gaps:
            console.print(f"    [{WARN_COLOR}]> {gap}[/{WARN_COLOR}]")
        console.print()

    # ── Escalation Events ──
    esc_events = summary.get("escalation_events", [])
    if esc_events:
        console.print(f"  [bold {ERROR_COLOR}]Escalations:[/bold {ERROR_COLOR}]")
        for event in esc_events:
            if isinstance(event, dict):
                cat = event.get("category", "").replace("_", " ")
                reason = event.get("reason", "")
                console.print(f"    [{ERROR_COLOR}]> [{cat}] {reason}[/{ERROR_COLOR}]")
            else:
                console.print(f"    [{ERROR_COLOR}]> {event}[/{ERROR_COLOR}]")
        console.print()

    # ── Next action ──
    next_action = summary.get("recommended_next_action", "")
    if next_action:
        console.print(f"  [bold green]Next Action:[/bold green]  {next_action}")

    console.print()
    console.print(Rule(style=ACCENT_DIM))
    console.print()


def print_token_usage():
    """Print token usage stats in a compact format."""
    usage = get_token_usage()
    if usage["total"] > 0:
        console.print(
            f"  [{MUTED}]Tokens — prompt: {usage['prompt']:,}  "
            f"completion: {usage['completion']:,}  "
            f"total: {usage['total']:,}[/{MUTED}]"
        )
        console.print()


def main():
    """Run the interactive CLI conversation."""
    print_header()

    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        console.print(f"\n[bold {ERROR_COLOR}]Configuration Error:[/bold {ERROR_COLOR}] {e}")
        sys.exit(1)

    # Initialize conversation manager
    manager = ConversationManager()

    # Print greeting
    greeting = manager.start_session()
    tag = _stage_tag("faq_answering")
    console.print(Panel(
        greeting,
        border_style=ACCENT_DIM,
        box=box.ROUNDED,
        title=tag,
        title_align="left",
        padding=(1, 3),
    ))

    # Set up graceful shutdown
    def signal_handler(sig, frame):
        console.print(f"\n  [{MUTED}]Generating summary...[/{MUTED}]")
        try:
            _, metadata = manager.process_message("/summary")
            if metadata.get("summary"):
                print_summary(metadata["summary"])
        except Exception:
            pass
        print_token_usage()
        console.print(f"[{MUTED}]Session ended.[/{MUTED}]\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # ── Main conversation loop ───────────────────────────────────────────
    while True:
        try:
            console.print()
            user_input = console.input(f"[bold {USER_COLOR}]You >>[/bold {USER_COLOR}] ")
        except (EOFError, KeyboardInterrupt):
            signal_handler(None, None)
            break

        if not user_input.strip():
            continue

        # Process the message
        try:
            response, metadata = manager.process_message(user_input)
        except Exception as e:
            console.print(f"\n  [bold {ERROR_COLOR}]Error:[/bold {ERROR_COLOR}] {e}")
            console.print(f"  [{MUTED}]Try again or type /quit to exit.[/{MUTED}]")
            continue

        # Display the response
        print_ai_response(response, metadata)

        # If session ended, print summary and exit
        if metadata.get("session_ended"):
            if metadata.get("summary"):
                print_summary(metadata["summary"])
            print_token_usage()
            console.print(f"[{MUTED}]Session ended. Thank you for using Closira AI.[/{MUTED}]\n")
            break

        # If qualification complete, show the summary
        if metadata.get("all_complete") and metadata.get("qualification_summary"):
            qual = metadata["qualification_summary"]
            console.print()
            qual_text = Text()
            qual_text.append("Lead Qualification Complete\n\n", style="bold")
            qual_text.append(f"Service:    ", style="bold")
            qual_text.append(f"{qual.get('recommended_service', 'N/A')}\n")
            qual_text.append(f"Urgency:    ", style="bold")
            qual_text.append(f"{qual.get('urgency', 'N/A')}\n")
            qual_text.append(f"Next Step:  ", style="bold")
            qual_text.append(f"{qual.get('next_step', 'N/A')}")

            console.print(Panel(
                qual_text,
                border_style="green",
                box=box.ROUNDED,
                title=Text(" QUALIFIED ", style="bold white on green"),
                title_align="left",
            ))


if __name__ == "__main__":
    main()
