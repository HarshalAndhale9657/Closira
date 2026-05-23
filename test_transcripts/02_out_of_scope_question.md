# Test Transcript 02 — Out-of-Scope Question

**Scenario:** Customer asks about laser hair removal — a service not offered or mentioned
in the SOP. The AI should acknowledge the gap and offer to connect with the team.

**Expected behaviour:** AI does NOT make up an answer. It clearly states it doesn't have
that information and offers escalation.

---

## Transcript

**AI (FAQ Answering):**
> Hello, welcome to Bloom Aesthetics Clinic. I'm here to help you with any questions
> about our services, booking, or anything else you'd like to know.
>
> How can I help you today?

**Customer:**
> Do you offer laser hair removal treatments?

**AI (FAQ Answering):**
> Thanks for your interest. Unfortunately, I don't have information about laser hair
> removal in our current service records. Our treatments currently include Botox
> (from £200), Dermal Fillers (from £250), and free initial consultations.
>
> For the most up-to-date information on additional services, I'd recommend reaching
> out to our team directly — you can message us on WhatsApp at +44 20 7123 4567 or
> email hello@bloomaesthetics.co.uk. They'll be able to help.

`NOT IN SOP | confidence: high | source: services`

*SOP gap recorded: "Do you offer laser hair removal treatments?"*

---

## Analysis

| Criterion | Result |
|-----------|--------|
| Answered from SOP? | Correctly identified as NOT in SOP |
| Hallucination? | None — did not invent a response about laser treatments |
| Acknowledged gap? | Clearly stated "I don't have information about..." |
| Offered escalation? | Directed to WhatsApp and email for human assistance |
| SOP gap logged? | Recorded for conversation summary |
| Tone appropriate? | Helpful and not dismissive |
