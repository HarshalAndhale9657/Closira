# Test Transcript 05 — Conversation Summary

**Scenario:** A complete end-to-end session covering FAQ answering, an out-of-scope
question, and session termination. The AI generates a structured conversation summary
at the end capturing intent, details, SOP gaps, and recommended actions.

**Expected behaviour:** Clean, structured summary with all fields populated accurately
from the actual conversation — no fabricated details.

---

## Transcript

**AI (FAQ Answering):**
> Hello, welcome to Bloom Aesthetics Clinic. I'm here to help you with any questions
> about our services, booking, or anything else you'd like to know.
>
> How can I help you today?

**Customer:**
> Hi, I'm interested in getting lip fillers. How much do they cost?

**AI (FAQ Answering):**
> Our Dermal Fillers start from £250 and can be used for lip enhancement, cheek
> augmentation, nasolabial folds, and jawline contouring. The treatment takes 30–45
> minutes, and results are immediate with full results showing after 1–2 weeks once
> any swelling subsides.
>
> Fillers typically last 6–12 months depending on the area and product used. Would you
> like to book a free consultation to discuss your options?

`SOP | confidence: high | source: services`

**Customer:**
> That sounds good. Do you offer any monthly payment plans for it?

**AI (FAQ Answering):**
> That's a great question. Unfortunately, I don't have detailed information about
> monthly payment plans in our current records. I'd recommend reaching out to our team
> directly for the most up-to-date information on financing options — you can message
> us on WhatsApp at +44 20 7123 4567.
>
> We do accept cash, debit card, credit card, and bank transfer for payment on the day.

`NOT IN SOP | confidence: medium | source: policies`

*SOP gap recorded: "Do you offer any monthly payment plans for it?"*

**Customer:**
> OK thanks. What are your opening hours?

**AI (FAQ Answering):**
> We're open Monday to Saturday, 9:00 AM to 7:00 PM. We're closed on Sundays and bank
> holidays. Is there anything else I can help you with?

`SOP | confidence: high | source: hours`

**Customer:**
> That's all for now, bye!

---

## Conversation Summary

```
────────────────── Conversation Summary ──────────────────

Intent:  Interested in lip filler treatments, enquired about pricing and payment plans.

  Detail                    Value
 ─────────────────────────  ──────────────────────────────────
  Treatment Interest        Dermal Fillers (lip enhancement)
  Experience Level          Not discussed
  Preferred Timing          Not discussed
  Budget Mentioned          Yes (asked about payment plans)
  Contact Info Provided     No
  Additional Notes          Checked opening hours

  SOP Gaps:
    > Customer asked about monthly payment plans — not covered in SOP

  Next Action:  Follow up with information about payment plan options. Encourage
                booking a free consultation to discuss lip filler treatment.

──────────────────────────────────────────────────────────
```

---

## Summary JSON Output

```json
{
  "customer_intent": "Interested in lip filler treatments, enquired about pricing and payment plans",
  "key_details": {
    "treatment_interest": "Dermal Fillers (lip enhancement)",
    "experience_level": "Not discussed",
    "preferred_timing": "Not discussed",
    "budget_mentioned": true,
    "contact_info_provided": false,
    "additional_notes": "Checked opening hours (Mon-Sat, 9am-7pm)"
  },
  "sop_gaps": [
    "Customer asked about monthly payment plans — not covered in SOP"
  ],
  "escalation_events": [],
  "customer_sentiment": "positive",
  "recommended_next_action": "Follow up with information about payment plan options. Encourage booking a free consultation to discuss lip filler treatment in detail."
}
```

---

## Analysis

| Criterion | Result |
|-----------|--------|
| Intent captured correctly? | "Interested in lip fillers" — matches conversation |
| Key details accurate? | All fields reflect actual conversation content |
| SOP gaps identified? | Payment plans flagged as a gap |
| No fabricated details? | "Not discussed" used for fields that weren't covered |
| Actionable next step? | Specific follow-up recommendation |
| Escalation events? | Correctly empty — no escalation occurred |
