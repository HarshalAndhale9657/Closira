# Test Transcript 01 — In-SOP Question

**Scenario:** Customer asks about Botox prices — a question directly covered by the SOP.
The AI should answer accurately from the SOP data only.

**Expected behaviour:** AI provides the correct price (from £200) and cites the services section.

---

## Transcript

**AI (FAQ Answering):**
> Hello, welcome to Bloom Aesthetics Clinic. I'm here to help you with any questions
> about our services, booking, or anything else you'd like to know.
>
> How can I help you today?

**Customer:**
> What are your Botox prices?

**AI (FAQ Answering):**
> Great question. Our Botox (anti-wrinkle injection) treatments start from £200. The final
> price depends on the number of areas you'd like treated — for example, forehead lines,
> frown lines, or crow's feet.
>
> We'd be happy to give you a personalised quote during a free consultation. Would you like
> to book one?

`SOP | confidence: high | source: services`

---

## Analysis

| Criterion | Result |
|-----------|--------|
| Answered from SOP? | Yes — price matches SOP ("from £200") |
| Hallucination? | None — all details are in the SOP |
| Source cited? | Services section |
| Tone appropriate? | Warm, professional, ends with next step |
| Clear next action? | Suggests booking a consultation |
