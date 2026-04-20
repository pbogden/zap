# Make Scenario — Framer Demo

The Make scenario for this demo is functionally identical to the one described
in [Stage 2 of the Flask demo](../../docs/stage2.md). If you've already built
that scenario, you can use the same one here — the webhook payload from Framer
has the same shape as the payload from `leads.py`.

This document covers only what's different.

---

## What's the same as Stage 2

- The Custom Webhook trigger module
- The HubSpot Create/Update Contact module and field mappings
- The Gmail confirmation email to the prospect
- The optional Slack notification to `#leads`
- The free plan compatibility (webhooks fire instantly, not on a schedule)

If you're building this scenario for the first time, follow
[Stage 2's Make setup guide](../../docs/stage2.md) — it covers every step
in detail. Come back here for the one difference below.

---

## What's different: teaching Make the payload

In the Flask demo, you taught Make the payload structure by submitting the
form on your running Flask app. In this demo, you teach Make by submitting
the Framer form on your published site.

The sequence is:

1. Create the Make scenario and add a Custom Webhook trigger
2. Copy the webhook URL
3. **Paste it into Framer's Send To → Webhook field** (see [framer-setup.md](framer-setup.md))
4. Publish the Framer site
5. Submit the form once with any test data
6. Return to Make — click **Re-determine data structure**
7. Make will have received the payload and mapped `name`, `email`,
   `company`, and `message` as available fields
8. Continue building the rest of the scenario

---

## The payload Make receives

```json
{
  "name": "Jordan Kim",
  "email": "jordan@example.com",
  "company": "Cascade Industrial",
  "message": "We're evaluating security vendors for a zero-trust rollout..."
}
```

This is exactly the same structure as the Flask demo sends. The HubSpot
and Slack module configurations are therefore identical — field mappings,
message templates, everything.

---

## Using the same scenario for both demos

If you're running both demos in the same class, you don't need two separate
Make scenarios. One Custom Webhook scenario handles both — Flask's
`fire_webhook()` and Framer's form webhook both POST to the same URL with
the same payload shape.

This is worth making explicit to students:

> *"Same Make scenario. Different tools triggering it. Make is indifferent
> to where the webhook comes from — it just receives JSON and acts on it."*

That's the core lesson of running both demos together.
