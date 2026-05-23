# Test Transcript 03 — Escalation Trigger

**Scenario:** Customer expresses frustration and anger about wait times. The AI should
detect the negative sentiment and escalate to a human agent with a logged reason.

**Expected behaviour:** AI detects frustration/complaint sentiment, triggers escalation,
responds with empathetic handoff, and logs the event.

---

## Transcript

**AI (FAQ Answering):**
> Hello, welcome to Bloom Aesthetics Clinic. I'm here to help you with any questions
> about our services, booking, or anything else you'd like to know.
>
> How can I help you today?

**Customer:**
> Hi, I've been trying to get through to someone for days and nobody is responding.
> This is getting really frustrating. I booked an appointment last week and I still
> haven't received a confirmation. This is ridiculous!

```
ESCALATION  [COMPLAINT]
Reason: Customer is expressing strong frustration and dissatisfaction about
        unresponsive communication and a missing appointment confirmation.
```

**AI (Escalation):**
> I understand this is important to you, and I want to make sure you get the best
> help possible. Let me connect you with a member of our team who can assist you
> further. A team member will be with you shortly.

---

## Escalation Log Entry

```json
{
  "reason": "Customer is expressing strong frustration and dissatisfaction about unresponsive communication and a missing appointment confirmation.",
  "category": "complaint",
  "trigger_message": "Hi, I've been trying to get through to someone for days and nobody is responding. This is getting really frustrating. I booked an appointment last week and I still haven't received a confirmation. This is ridiculous!",
  "sentiment": "angry",
  "timestamp": "2026-05-23T12:00:00.000000"
}
```

---

## Analysis

| Criterion | Result |
|-----------|--------|
| Frustration detected? | Correctly identified "frustrated", "ridiculous" as angry sentiment |
| Escalation triggered? | `should_escalate: true` |
| Category correct? | Classified as "complaint" |
| Empathetic handoff? | Acknowledged importance, offered human connection |
| Event logged? | Written to escalation_log.json with full details |
| AI avoided resolving complaint itself? | Did not attempt to explain or fix the issue |
