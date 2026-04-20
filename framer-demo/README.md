# Framer Demo — Contact Form → Make → HubSpot + Slack

This demo produces the exact same outcome as [Stage 2 of the Flask demo](../README.md):
a contact form submission flows into HubSpot and triggers a Slack notification.

The difference is how it gets there. There is no Flask app, no Python, no server,
and no `fire_webhook()` call. The webhook fires from a GUI setting in Framer.
Make's scenario is identical.

---

## The Point

This demo exists to make one argument concrete:

> Make doesn't care where the webhook comes from.

The same Make scenario that receives a payload from `leads.py` in the Flask demo
works without modification when the payload comes from Framer. The integration
layer is decoupled from the tool that triggers it.

That's the practical version of [design-decisions.md Principle 2](../docs/design-decisions.md):
*Flask owns the data and the UX. Make owns the integrations.* Swap Flask for Framer
and the sentence still holds — because Make is the constant.

---

## What You Need

| Tool | Plan | Cost | Credit card? |
|---|---|---|---|
| Framer | Free | $0 | No |
| Make.com | Free | $0 | No |
| HubSpot | Free CRM | $0 | No |
| Slack | Free | $0 | No |

Total: $0, no payment method required.

---

## What Gets Built

A single-page Framer site with a contact form. When the form is submitted:

1. Framer POSTs the field values as JSON to a Make webhook URL
2. Make receives the payload and runs a scenario that:
   - Creates or updates a contact in HubSpot
   - Sends a Slack notification to `#leads`

```
Visitor submits form
        │
        │  POST { name, email, company, message }
        ▼
Framer  ──────────────────────────────────────────►  Make webhook
(no backend, no code)                                     │
                                                          ├──► HubSpot: Create contact
                                                          └──► Slack: Notify #leads
```

Compare to the Flask version:

```
Visitor submits form
        │
        ▼
Flask (leads.py)
  - Validates input
  - Writes to SQLite          ← this step doesn't exist in Framer
  - Calls fire_webhook()
        │
        │  POST { name, email, company, message }
        ▼
Make webhook  ──────────────────────────────────────►  HubSpot + Slack
```

The payload and everything to the right of the webhook is identical.
The left side — form handling, validation, persistence — is where they diverge.

---

## Setup

1. [Build and publish the Framer site](docs/framer-setup.md)
2. [Build the Make scenario](docs/make-scenario.md)

The full comparison between the two approaches is in [docs/comparison.md](docs/comparison.md).

---

## What This Demo Doesn't Have (And Why)

**No database write.** Framer has no backend storage, so submissions exist only
in Make's execution history and wherever Make sends them (HubSpot, in this case).
If Make is down when a form is submitted, the lead is gone. The Flask demo avoids
this by writing to SQLite before firing the webhook.

**No server-side validation.** Framer's form validation is client-side only — a
determined user can bypass it. The Flask demo validates in Python before anything
is stored or sent.

**No `webhook_fired` flag.** Because there's no database, there's no record of
whether Make was notified. You can't query "which submissions didn't reach Make?"

These aren't complaints about Framer — they're the trade-offs you accept when you
choose a no-code tool over a backend. For a marketing contact form on a low-traffic
site, they're usually acceptable. For a lead capture system where no lead can be
lost, the Flask pattern is the right choice.

That's the conversation this demo is designed to start.

---

## Is Make Actually Necessary Here?

No — and that's worth knowing.

Framer has native integrations for HubSpot, Google Sheets, and email. For
the core Sentinel requirement (lead capture → HubSpot), you could skip Make
entirely and wire Framer directly to HubSpot in about three clicks. No
webhook, no scenario, no Make account.

**So why use Make in this demo?**

The reason is pedagogical, not practical. The entire argument of this demo
is that Make is indifferent to where a webhook comes from — Flask or Framer,
it doesn't matter. That lesson only works if Make is present in both demos.
If you replace it with Framer's native HubSpot connector, you lose the
comparison entirely.

There's also a visibility argument: native integrations are invisible.
When Framer sends directly to HubSpot, there's no payload to inspect, no
execution history to read, no intermediate step you can pause and examine.
Make's visual execution trace is what makes the integration *teachable*.

**The honest production answer:** For a real Sentinel delivery, you'd
evaluate whether Framer's native HubSpot connector is sufficient before
reaching for Make. It probably is for Stage 2. Make earns its place in
Stage 3 (the approval workflow), where there's no native Framer equivalent
and human-in-the-loop logic genuinely needs an orchestration layer.

This is a good thing to say out loud in class:

> *"We're routing through Make here to make the data flow visible and to
> keep both demos comparable. In a real project, always ask whether a
> native connector eliminates a moving part — fewer moving parts is usually
> better."*
