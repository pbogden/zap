# Design Decisions

This document captures the architectural principles behind the demo — the
choices that recur across all three stages and are worth carrying into the
next project. Each one has a concrete expression somewhere in the codebase.

---

## 1. Your system of record never depends on an external service

**The principle:** Write to your own database before firing any webhook. If the
external service is unreachable, your data is still safe.

**Where this comes from:** This is the **Outbox Pattern**, documented in
*Enterprise Integration Patterns* (Hohpe & Woolf, 2003). The name comes from
the email metaphor: you drop a message in your outbox before handing it to the
mail carrier. If the carrier is unavailable, the message waits — it isn't lost.
The underlying reason is the CAP theorem: in any distributed system, network
partitions will happen, and your local state should remain consistent regardless.
Today this pattern appears throughout cloud-native architecture guidance — AWS,
Azure, and GCP all document it as a standard approach for reliable event
publishing. Tools like Debezium (change data capture) automate the outbox relay
at scale. The core rule hasn't changed; the infrastructure around it has.

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

**Where this comes from:** **Hexagonal Architecture** (Alistair Cockburn, 2005),
also called Ports and Adapters. The core idea is that your application should be
equally drivable by users, tests, or external systems — and equally indifferent
to which LinkedIn SDK, email provider, or CRM is plugged in on the other side.
The Flask/Make boundary is a port in Cockburn's sense: a defined interface that
either side can be swapped without touching the other. Robert Martin's **Clean
Architecture** (2017) extends the same principle under the name "dependency
rule" — dependencies should point inward, toward the core, never outward toward
infrastructure. In modern practice this shows up in how frameworks are designed:
FastAPI's dependency injection system and Django REST Framework's serializer
layer are both port-and-adapter patterns, even if they don't use that name.
It's also the instinct behind separating business logic from route handlers —
something AI code generators often skip, and something worth enforcing in review.

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

**See it in practice:** The [Framer demo](../framer-demo/README.md) replaces
Flask entirely with a no-code tool — but the Make scenario is unchanged. The
boundary holds even when one side of it disappears. The
[Flask vs. Framer comparison](../framer-demo/docs/comparison.md) shows exactly
what moves across that boundary and what doesn't.

---

## 3. Push and pull are both valid — know when to use each

**The principle:** There are two ways to connect your app to an automation
platform. Push means your app initiates the exchange (webhook). Pull means the
platform polls your app on a schedule (RSS, API endpoint). Each has a different
trade-off profile.

**Where this comes from:** *Enterprise Integration Patterns* (Hohpe & Woolf)
catalogues both as first-class patterns: **Event-Driven Consumer** (push) and
**Polling Consumer** (pull). The "dumb pipes, smart endpoints" principle — coined
in early microservices writing and popularized by Martin Fowler — favors push for
internal service-to-service communication precisely because it keeps the
transport layer simple. RSS's longevity is a data point in favor of pull for
public, ecosystem-facing interfaces: a stateless feed that any compliant reader
can consume is more durable than a custom webhook contract. In modern practice,
every major SaaS platform — Stripe, GitHub, Twilio, Make — offers both models,
and choosing between them is a routine design decision. Event-driven architecture
(AWS EventBridge, Azure Event Grid, Google Pub/Sub) is the scaled-up version of
the same push pattern used here.

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

**Where this comes from:** Two sources converge here. **The Fallacies of
Distributed Computing** (Peter Deutsch, 1994) lists eight assumptions developers
incorrectly make about networks — starting with "the network is reliable." The
timeout-and-catch pattern in `make_webhook.py` is a direct response to fallacies
1 and 2. **Release It!** (Michael Nygard, 2007) translates that into concrete
stability patterns: timeouts prevent slow dependencies from consuming all your
threads; bulkheads isolate failures so one service going down doesn't cascade.
The 12-Factor App (Heroku, 2011) makes the same point architecturally: treat
every backing service — including third-party APIs — as an attached resource that
can be detached and replaced. These ideas are now standard in cloud-native
engineering: circuit breakers and retries are first-class primitives in Kubernetes
service meshes (Istio, Linkerd), and Google's **Site Reliability Engineering**
book (2016) builds an entire discipline around the same instinct. Chaos
engineering — deliberately injecting failures to test resilience, pioneered by
Netflix — is the operational expression of taking these fallacies seriously.

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

**Where this comes from:** Donald Knuth's **Literate Programming** (1984)
proposed that programs should be written primarily for human readers, with the
machine execution as a side effect. The practical descendant of that idea is the
observation — attributed most often to Martin Fowler — that "any fool can write
code that a computer can understand; good programmers write code that humans can
understand." In a teaching demo, that obligation is heightened: the reader is
also a learner, and the *why* is as important as the *what*. In 2025 this
principle has a new dimension: AI coding assistants generate syntactically
correct code that often omits the *why* entirely. The ability to read that code
critically, identify missing intent, and add explanation where it matters is
increasingly the skill that distinguishes a developer from a prompt submitter.
Code that teaches is also code that AI can maintain — comments explaining a
constraint or invariant are exactly what a model needs to not break it later.

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

---

## Further reading

| Principle | Source |
|---|---|
| Outbox Pattern, Polling/Event-Driven Consumer | Hohpe & Woolf, *Enterprise Integration Patterns* (2003) — [enterpriseintegrationpatterns.com](https://www.enterpriseintegrationpatterns.com) |
| CAP theorem | Eric Brewer, "Towards Robust Distributed Systems," PODC keynote (2000) |
| Hexagonal Architecture (Ports and Adapters) | Alistair Cockburn, [alistair.cockburn.us/hexagonal-architecture](https://alistair.cockburn.us/hexagonal-architecture/) (2005) |
| Clean Architecture / Dependency Rule | Robert C. Martin, *Clean Architecture* (2017) |
| Fallacies of Distributed Computing | Peter Deutsch et al., Sun Microsystems (1994) — widely reproduced; see [wikipedia](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing) |
| Stability patterns (timeouts, bulkheads) | Michael Nygard, *Release It!* (2007; 2nd ed. 2018) |
| Twelve-Factor App | Heroku engineering, [12factor.net](https://12factor.net) (2011) |
| Dumb pipes, smart endpoints | Martin Fowler & James Lewis, "Microservices" (2014) — [martinfowler.com/articles/microservices.html](https://martinfowler.com/articles/microservices.html) |
| Literate Programming | Donald Knuth, *Literate Programming* (1984); CSLI Publications (1992) |
| Site Reliability Engineering | Beyer et al., *Site Reliability Engineering* (Google, 2016) — [sre.google/sre-book](https://sre.google/sre-book/table-of-contents/) |
| Chaos Engineering | Rosenthal et al., *Chaos Engineering* (O'Reilly, 2020); originated at Netflix |
