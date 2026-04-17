# Design Decisions

This document captures the architectural principles behind the demo — the
choices that recur across all three stages and are worth carrying into the
next project. Each one has a concrete expression somewhere in the codebase.

---

## 1. Your system of record never depends on an external service

**The principle:** Write to your own database before firing any webhook. If the
external service is unreachable, your data is still safe.

**Where it appears:** `leads.py` and `case_studies.py` both follow this pattern:

```python
# 1. Save to database first — this always happens
db.execute("INSERT INTO lead (...) VALUES (...)", (...))
db.commit()

# 2. Fire webhook to Make — this may silently fail
webhook_fired = fire_webhook("LEAD_CAPTURE", { ... })

# 3. Record whether Make was notified
db.execute("UPDATE lead SET webhook_fired = ? WHERE id = ?",
           (1 if webhook_fired else 0, lead_id))
```

The `webhook_fired` column isn't just a debugging aid — it's an assertion about
ownership. The database is the source of truth. Make is a downstream consumer.
If Make is down, the lead still exists and can be replayed later.

**The broader instinct:** Any time your application depends on a third-party
service to complete a user-facing action, ask: what happens when that service
is unavailable? The answer should never be "the user's data is lost."

---

## 2. Flask owns the data and the UX. Make owns the integrations.

**The principle:** Draw a clear boundary between what your application is
responsible for and what the automation layer is responsible for. Don't blur it.

**Where it appears:** In every stage, Flask handles validation, persistence,
and the HTTP response. Make handles everything that crosses a system boundary —
LinkedIn, Slack, HubSpot, email. Flask doesn't import a LinkedIn SDK. Make
doesn't touch your database.

```
Flask                          Make
─────────────────────────────────────────────────────
Form validation                LinkedIn API
Database writes                Slack API
Flash messages                 HubSpot contact creation
HTTP responses                 Email delivery
Session management             Approval workflows
```

**Why this matters:** When requirements change — and they always do — the
boundary determines how much of your system is affected. If Sentinel switches
from HubSpot to Salesforce, that's a Make configuration change. It doesn't
touch Flask, doesn't require a deployment, and doesn't risk breaking anything
else. If you'd built the HubSpot integration natively in Flask, it's a code
change, a PR, a test run, and a deployment.

**The corollary:** Business logic that can change without a code deploy should
live outside your codebase. Business logic that must be reliable, auditable,
and version-controlled should live inside it.

---

## 3. Push and pull are both valid — know when to use each

**The principle:** There are two ways to connect your app to an automation
platform. Push means your app initiates the exchange (webhook). Pull means the
platform polls your app on a schedule (RSS, API endpoint). Each has a different
trade-off profile.

**Where it appears:** The blog uses both. `blog.py` fires a webhook on publish
(push) and also serves an RSS feed at `/feed` (pull). The Stage 1 docs walk
through both approaches and when to reach for each.

| | Push (webhook) | Pull (RSS / polling) |
|---|---|---|
| Timing | Immediate | Delayed by poll interval |
| Initiator | Your app | The external platform |
| Your app needs to be running | At publish time | At poll time |
| Works with RSS readers / newsletter tools | No | Yes |
| Good for | Real-time notifications | Feed aggregators, newsletters |

**The deeper point:** Push feels more modern and is often the right default for
internal integrations. But pull — specifically RSS — has survived 25 years
because it's simple, stateless, and works with an enormous ecosystem of tools
without any configuration on your end. Mailchimp, Substack, Buttondown, and
most newsletter platforms can drive an RSS-to-email campaign directly from
`/feed` with no Make scenario required.

Understanding both models makes you more flexible when a client says "we already
use Mailchimp" — you don't have to rebuild the Stage 1 scenario, you just point
them at the feed.

---

## 4. Make is a dependency. Treat it like one.

**The principle:** Any third-party service — Make, HubSpot, Slack, LinkedIn —
is a dependency your application doesn't control. Acknowledge that explicitly
in how you build.

**Where it appears:** `make_webhook.py` catches all exceptions and returns a
boolean. The calling code in each blueprint stores the result. The app never
crashes because Make is unreachable.

```python
def fire_webhook(event_type: str, payload: dict) -> bool:
    ...
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Webhook error ({event_type}): {e}")
        return False
```

**What this buys you:** Resilience at the boundary. The 5-second timeout means
a slow Make response doesn't hold up the user's HTTP request. The caught
exception means a Make outage doesn't surface as a 500 error. The boolean return
means the caller can decide what to do with the outcome.

**What to think about next:** This implementation is fire-and-forget with
logging. A production system might want a retry queue — store failed webhooks
in a `webhook_retry` table and replay them on a schedule. That's a natural
extension if the lesson plan develops in that direction.

---

## 5. Readable code is part of the deliverable

**The principle:** In a teaching context, the code itself is documentation.
Choices that would be implicit in a production codebase should be made explicit
here.

**Where it appears:** Throughout the codebase:

- `# STAGE 1` comments in `blog.py` mark the two lines that were added to the
  Flaskr base, so students can see exactly what changed and why.
- Module docstrings in `leads.py`, `case_studies.py`, and `make_webhook.py`
  explain the design intent, not just what the code does.
- `schema.sql` seeds three realistic case studies so the app is demonstrable
  immediately, without setup steps that distract from the concepts.
- The `webhook_fired` column exists partly to make the local-first principle
  visible — it's a concrete, queryable artifact of the design decision.

**The broader point:** When you're building something that other people will
learn from, the gap between "it works" and "it teaches" is usually in the
explanation of *why*, not the description of *what*.
