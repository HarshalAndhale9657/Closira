# Prompt Design Document — Closira AI Customer Support Workflow

## Overview

This document details the prompt engineering strategy for the Closira AI customer support
workflow powering **Bloom Aesthetics Clinic**. The system uses OpenAI GPT-4o with carefully
crafted prompts to handle FAQ answering, lead qualification, escalation detection, and
conversation summarisation.

---

## 1. System Prompt — FAQ Answering (Stage 1)

### Full Prompt

```
You are the AI customer support assistant for Bloom Aesthetics Clinic.
Your role is to answer customer questions warmly, professionally, and accurately.

## CRITICAL RULES — READ CAREFULLY

1. **ONLY answer from the SOP data provided below.** Do NOT invent, assume, guess, or
   infer ANY information that is not explicitly stated in the SOP.
2. If the customer asks something NOT covered in the SOP, you MUST say you don't have
   that information and offer to connect them with a team member. NEVER make up an answer.
3. Always cite which section of the SOP your answer comes from (services, booking,
   policies, etc.).
4. If you are uncertain whether the SOP covers the question, err on the side of caution:
   say "I don't have that specific information in our records" and offer escalation.

## TONE & PERSONA
- Warm, professional, and reassuring
- Conversational but polished — avoid overly clinical or casual language
- Acknowledge the customer's concerns before answering
- Keep responses concise and scannable (customers message on mobile)
- End with a clear next step (e.g., booking a consultation)

## SOP DATA
[Full SOP data injected here — see sop_data.json]

## RESPONSE FORMAT
You MUST respond with a JSON object in this exact format:
{
    "answer": "Your natural-language response to the customer",
    "confidence": "high" | "medium" | "low",
    "source_section": "The SOP section this answer comes from",
    "in_sop": true | false
}
```

### Design Reasoning

| Decision | Rationale |
|----------|-----------|
| **"CRITICAL RULES" header** | Places the most important constraints at the top where they have maximum impact on model attention |
| **Negative instructions ("Do NOT invent...")** | Research shows explicit negative instructions are more effective than positive-only framing for preventing hallucination |
| **Citation requirement** | Forcing the model to cite a source section creates an accountability mechanism — if it can't name a source, it's more likely to flag the answer as out-of-SOP |
| **JSON response format** | Structured output enables reliable programmatic parsing; GPT-4o's native JSON mode ensures valid JSON |
| **"Err on the side of caution" instruction** | Establishes a clear default behaviour for ambiguous cases — fail safe rather than fail creative |
| **Tone section** | Calibrated for SMB context — customers expect warmth and efficiency, not corporate formality or clinical detachment |

---

## 2. Hallucination Prevention

### Strategy

Hallucination prevention is implemented through **multiple reinforcing layers**:

#### Layer 1: Prompt-Level Grounding
- **Explicit boundary**: *"ONLY answer from the SOP data provided below"*
- **Explicit prohibition**: *"Do NOT invent, assume, guess, or infer"*
- **Fail-safe instruction**: *"If you are uncertain... err on the side of caution"*
- **Canary response**: A specific phrase the model should use when unsure:
  *"I don't have that specific information in our records"*

#### Layer 2: Structural Enforcement
- **Source citation requirement**: Every answer must include `source_section`,
  creating a self-verification step where the model must identify where the answer
  came from. If it can't, the answer is likely hallucinated.
- **Binary SOP flag**: The `in_sop: true/false` field forces an explicit
  classification decision before generating the answer.
- **Confidence scoring**: The `confidence` field provides a secondary signal —
  `low` confidence triggers escalation regardless of other factors.

#### Layer 3: Model Configuration
- **Temperature: 0.2** — Low temperature significantly reduces creative generation
  and makes the model more likely to stick to provided information.
- **JSON mode**: Native JSON output mode reduces the chance of the model "drifting"
  into conversational responses that bypass structured checks.

#### Layer 4: Application-Level Safety Net
- Responses with `in_sop: false` are tracked as **SOP gaps**
- After **2+ consecutive unanswered questions**, the system automatically escalates
  to a human agent — this prevents the model from being repeatedly pressed on topics
  it shouldn't answer
- All SOP gaps are recorded and included in the conversation summary for the team

### Why This Works
Each layer catches different failure modes:
- **Layer 1** prevents most hallucinations at generation time
- **Layer 2** catches cases where the model generates a confident-sounding but
  ungrounded answer (it would need to fabricate a source section too)
- **Layer 3** reduces the statistical likelihood of creative generation
- **Layer 4** provides a runtime safety net for cases that slip through

---

## 3. Confidence-Based Escalation

### Detection Approach

Escalation detection runs as a **parallel classifier** on every customer message.
This is a separate LLM call with its own specialised prompt, independent of the
main response generation. This ensures escalation detection is never skipped, even
during lead qualification or other stages.

### Escalation Triggers

| Trigger | Detection Method | Example |
|---------|-----------------|---------|
| Complaint / Frustration | Sentiment analysis via LLM | "This is ridiculous", "I've been waiting forever" |
| Medical question | Topic classification | "Is Botox safe during pregnancy?", "Will it interact with my medication?" |
| Pricing negotiation | Intent detection | "Can you do it cheaper?", "That's too expensive" |
| Explicit human request | Keyword + intent | "I want to speak to a manager", "Get me a real person" |
| Adverse reaction | Medical urgency detection | "My face is swollen since the treatment" |
| >2 unanswered questions | Counter-based (application logic) | Multiple consecutive out-of-SOP questions |
| Low confidence | Self-reported by FAQ stage | When the FAQ module returns `confidence: low` |

### Escalation Output Format

```json
{
    "should_escalate": true,
    "reason": "Customer expressed frustration about wait times",
    "category": "complaint",
    "sentiment": "angry",
    "confidence": "high"
}
```

### Why Parallel Classification?

Running escalation as a separate call (rather than embedding it in the FAQ prompt) provides:
1. **Reliability**: The classifier has a single, focused task — no competing objectives
2. **Consistency**: Uses very low temperature (0.1) for deterministic classification
3. **Stage independence**: Works regardless of whether the conversation is in FAQ, lead
   qualification, or any other stage
4. **Logging**: Clean separation makes it easy to log and audit escalation decisions

### Escalation Response
When escalated, the AI responds with an empathetic handoff message and logs the event:
```
"I understand this is important to you, and I want to make sure you get the best
help possible. Let me connect you with a member of our team who can assist you
further. A team member will be with you shortly."
```

---

## 4. Tone and Persona

### Persona Definition

The AI is positioned as a **friendly, knowledgeable receptionist** for an aesthetics
clinic — not a doctor, not a salesperson, not a chatbot.

### Tone Calibration

| Dimension | Setting | Rationale |
|-----------|---------|-----------|
| Formality | Conversational-professional | SMB customers expect warmth, not corporate jargon |
| Empathy | High | Aesthetics customers may feel vulnerable discussing appearance concerns |
| Brevity | Concise | Most customers are messaging from mobile; long paragraphs lose attention |
| Proactivity | Moderate | Suggest next steps (consultations, bookings) but don't push |
| Clinical knowledge | Refer, don't advise | Never give medical advice; always redirect to practitioners |
| Emoji usage | None or minimal | Professional tone without relying on emoji for warmth |

### Example Tone Comparison

**Too casual:** "Hey! Botox is like £200 btw, wanna book?"

**Too clinical:** "Botulinum toxin type A injections are available commencing at a price point of £200. Please refer to our booking portal."

**Correct:** "Great question. Our Botox treatments start from £200, and the final price depends on the number of areas you'd like treated. Would you like to book a free consultation to discuss your options?"

---

## 5. Lead Qualification Prompts

### Question Design

The three qualification questions are designed to extract maximum value with minimum friction:

1. **Treatment interest** — Maps directly to services for routing and pricing
2. **Experience level** — Determines whether to recommend consultation (first-timers) or direct booking
3. **Preferred timing** — Assesses urgency and enables proactive scheduling

### Transition Strategy

The system doesn't abruptly switch to "survey mode". Instead, after 2+ FAQ exchanges
where the customer shows purchase intent (detected via keyword matching), it transitions
naturally:

*"I'd love to help you take the next step. Let me ask you a couple of quick questions
so we can find the right fit for you."*

---

## 6. Summary Generation

The conversation summary prompt receives the full transcript and extracts structured
data. It uses the same grounding principle as the FAQ prompt: **do not invent details
not present in the conversation**.

The summary includes:
- **Customer intent**: What the customer wanted
- **Key details**: Treatment interest, experience, timing, budget mentions
- **SOP gaps**: Questions the AI couldn't answer
- **Escalation events**: Any escalation triggers fired
- **Recommended next action**: Specific follow-up for the team

This provides the human team with actionable intelligence from every AI conversation.
