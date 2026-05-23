# Test Transcript 04 — Lead Qualification

**Scenario:** Customer asks about services and shows interest. The AI transitions from
FAQ answering to lead qualification, asks structured questions, collects responses,
and produces a qualification summary.

**Expected behaviour:** AI asks 3 structured questions, extracts answers, and generates
a qualification summary with recommended service and next steps.

---

## Transcript

**AI (FAQ Answering):**
> Hello, welcome to Bloom Aesthetics Clinic. I'm here to help you with any questions
> about our services, booking, or anything else you'd like to know.
>
> How can I help you today?

**Customer:**
> Hi! I've been thinking about getting some anti-wrinkle treatment. What do you offer?

**AI (FAQ Answering):**
> Great to hear you're considering anti-wrinkle treatments. We offer Botox (anti-wrinkle
> injections) starting from £200. The treatment takes just 20–30 minutes, results are
> visible within 3–7 days, and typically last 3–4 months with minimal downtime.
>
> We also offer a free initial consultation where our practitioner can assess the areas
> you'd like treated and create a personalised plan.

`SOP | confidence: high | source: services`

**Customer:**
> That sounds great! I'd like to book a consultation.

**AI (FAQ Answering → Lead Qualification):**
> Wonderful, we'd love to help you book that in.
>
> I'd love to help you take the next step. Let me ask you a couple of quick questions
> so we can find the right fit for you.
>
> Which treatment are you most interested in? For example, Botox, fillers, or would you
> like a general consultation?

*--- Switched to QUALIFY stage ---*

**Customer:**
> Definitely Botox — mainly for my forehead lines.

**AI (Lead Qualification):**
> Botox for forehead lines — great choice, that's one of our most popular treatments.
>
> Have you had this type of treatment before, or would this be your first time?

*Extracted: treatment_interest = "Botox for forehead lines"*

**Customer:**
> This would be my first time, so I'm a bit nervous!

**AI (Lead Qualification):**
> That's completely understandable — and there's nothing to worry about. Our practitioners
> are very experienced and will walk you through everything during your free consultation.
>
> When would you ideally like to come in? Do you have a preferred day or time?

*Extracted: experience_level = "First time"*

**Customer:**
> I'm quite flexible, but ideally sometime next week, maybe a Wednesday or Thursday afternoon?

**AI (Lead Qualification):**
> Next week, Wednesday or Thursday afternoon — let me note that down.
>
> Thank you for answering those questions. Based on what you've shared, here's a quick summary:

*Extracted: preferred_timing = "Next week, Wednesday or Thursday afternoon"*

---

## Qualification Summary

```
QUALIFIED

Service:    Botox (Anti-Wrinkle Injections)
Urgency:    Medium
Next Step:  Book free consultation for next Wed/Thu afternoon
```

**Internal Summary:**
> First-time Botox patient interested in forehead line treatment. Flexible schedule,
> preferring next week Wednesday or Thursday afternoon. Recommend booking a free
> consultation as a first step — patient has expressed some nervousness so practitioner
> should focus on explaining the process and setting expectations.

---

## Analysis

| Criterion | Result |
|-----------|--------|
| Natural transition to qualification? | Triggered by purchase intent ("I'd like to book") |
| Questions asked one at a time? | Three questions asked sequentially |
| Answers extracted correctly? | All three fields populated |
| Conversational tone maintained? | Empathetic, acknowledged nervousness |
| Summary generated? | With recommended service, urgency, and next step |
