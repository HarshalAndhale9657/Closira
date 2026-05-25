# Closira AI — Customer Support Workflow

A Python-based AI customer support workflow for **Bloom Aesthetics Clinic**, demonstrating
SOP-grounded FAQ answering, lead qualification, escalation detection, and session summarisation.

Built using OpenAI GPT-4o with structured output, parallel escalation classification,
and a four-layer hallucination prevention strategy.

> **Assignment:** Closira AI Engineering Intern

---

## Architecture

```
Customer Input (CLI)
        |
        v
+------------------------------+
|    Conversation Manager       |  Orchestrator — routes each message
+-------+----------------------+
        |
   +----+----+
   |         |
   v         v
Escalation   Current Stage
Detector     +------------------+
(parallel)   | FAQ Answering    |  SOP-grounded, confidence-scored
             | Lead Qualify     |  Structured Q&A, answer extraction
             +------------------+
                     |
                     v  (session end)
              Conversation Summary
              Structured JSON output
```

**Key design decisions:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Provider | GPT-4o | Native JSON mode, strong instruction following |
| SOP injection | Full prompt injection | SOP is small (~6KB); no RAG overhead needed |
| Escalation | Parallel LLM classifier | Independent of main response; never skipped |
| Temperature | 0.2 (FAQ), 0.1 (escalation) | Minimises creative generation, maximises grounding |
| Output format | Structured JSON | Reliable parsing via native `response_format` |

---

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key

### Setup

```bash
# Clone and enter the project
git clone https://github.com/HarshalAndhale9657/Closira
cd BreakOut

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure your API key
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
# Edit .env and set OPENAI_API_KEY
```

### Run

```bash
python -m src
```

### CLI Commands

| Command | Action |
|---------|--------|
| `/status` | Show current conversation state |
| `/qualify` | Switch to lead qualification stage |
| `/summary` | End session and generate summary |
| `/quit` | End the session |
| `bye` / `exit` | End the session |

---

## Project Structure

```
.
├── README.md                          Setup, architecture, trade-offs
├── prompt_design.md                   Prompt engineering document
├── requirements.txt                   Python dependencies
├── .env.example                       API key template
├── sop_data.json                      SOP data (Bloom Aesthetics Clinic)
│
├── src/
│   ├── main.py                        CLI interface (Rich terminal UI)
│   ├── conversation_manager.py        Stage orchestrator
│   ├── config.py                      Configuration and settings
│   ├── models.py                      Data models (dataclasses, enums)
│   ├── sop_loader.py                  SOP loading and formatting
│   ├── llm_client.py                  OpenAI API wrapper
│   └── stages/
│       ├── faq_answering.py           Stage 1 — SOP-grounded Q&A
│       ├── lead_qualification.py      Stage 2 — Structured qualification
│       ├── escalation_detection.py    Stage 3 — Parallel classifier
│       └── conversation_summary.py    Stage 4 — Session summary
│
├── test_transcripts/                  Sample conversations (5 scenarios)
│   ├── 01_in_sop_question.md
│   ├── 02_out_of_scope_question.md
│   ├── 03_escalation_trigger.md
│   ├── 04_lead_qualification.md
│   └── 05_conversation_summary.md
│
└── logs/
    └── escalation_log.json            Runtime escalation log
```

---

## How It Works

### Stage 1: FAQ Answering

The AI answers customer questions **strictly from the SOP data**. Every response includes
a confidence score (`high` / `medium` / `low`) and a source citation. Questions not
covered by the SOP are flagged as gaps, and the customer is offered human assistance.

### Stage 2: Lead Qualification

After detecting purchase intent (keyword heuristic + exchange count), the AI transitions to
asking structured questions — treatment interest, experience level, and preferred timing.
Answers are extracted into structured fields and a qualification summary is generated.

### Stage 3: Escalation Detection

A parallel classifier runs on **every customer message** using a dedicated LLM call at
temperature 0.1. It detects:

- Complaints and expressions of frustration
- Medical questions requiring clinical judgment
- Pricing negotiation attempts
- Explicit requests for a human agent
- Mentions of adverse reactions
- Accumulated SOP gaps (>2 consecutive unanswered questions)

When triggered, the AI responds with an empathetic handoff and logs the event to
`logs/escalation_log.json`.

### Stage 4: Conversation Summary

At session end, the AI analyses the full transcript and produces a structured summary:
customer intent, key details collected, SOP gaps identified, escalation events, and a
recommended next action for the team.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >= 1.40.0 | GPT-4o API client |
| `python-dotenv` | >= 1.0.0 | Environment variable management |
| `rich` | >= 13.0.0 | Terminal UI — panels, tables, colour |

---

## Trade-offs and Limitations

| Area | Trade-off | Rationale |
|------|-----------|-----------|
| SOP retrieval | Full injection, no RAG | SOP is ~6KB; embedding search adds complexity without benefit |
| Escalation cost | Separate LLM call per message | Higher latency/cost, but ensures reliable independent detection |
| State management | In-memory only | Sufficient for CLI demo; production would use persistent storage |
| Stage transitions | Keyword heuristic | Simple but effective; production would use an LLM classifier |
| Streaming | Not implemented | Keeps code simple; streaming would improve perceived latency |

---

## Test Transcripts

See [`test_transcripts/`](test_transcripts/) for sample conversations demonstrating each
expected behaviour:

1. **In-SOP question** — Botox pricing answered accurately from SOP
2. **Out-of-scope question** — Laser hair removal gracefully flagged as unavailable
3. **Escalation trigger** — Frustrated customer detected, empathetic handoff
4. **Lead qualification** — Full structured Q&A flow with summary
5. **Conversation summary** — End-of-session structured output

---

## Prompt Design

See [`prompt_design.md`](prompt_design.md) for the complete prompt engineering document:

- System prompts with inline design reasoning
- Four-layer hallucination prevention strategy
- Confidence-based escalation logic
- Tone and persona calibration for SMB context
#
