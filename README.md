# Web App Integration Demo

A teaching demo built on the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/). Each stage adds a feature driven by a real functional requirement from a small startup client. For each requirement, we ask: what's the simplest approach that actually meets the need? The answer isn't always the same tool.

---

## The client

A small professional services firm — a few people, no dedicated technical staff, growing. They have a website with a blog. They want to reach more clients, capture leads, and share expertise without adding operational overhead.

---

## How to read this demo

Each stage starts with a **functional requirement** — what the client actually needs, in plain language. Then it explains why a particular approach was chosen over alternatives. The decision is the lesson, not just the code.

---

## Stage 1 — Blog: reaching an audience

**Requirement:** Content published on the blog should reach subscribers automatically, without the client manually distributing each post.

**Decision: RSS/Atom feed — no external service needed.**

The simplest answer is a feed at a predictable URL. Many newsletter platforms (Mailchimp, Buttondown, Substack) poll it on a schedule and distribute new posts automatically — you point them at the URL once and they handle the rest. Some platforms also support push via webhook if you prefer that approach; the choice of RSS here is about simplicity, not capability.

Sending an automatic notification the moment a post goes live only makes sense if two different people are involved: one who writes and publishes, and another who needs to be told so they can share it. For a small team where the same person does both, there's no one to notify who doesn't already know. Add notifications later if the team grows and that handoff becomes a real problem.

**New code:** `/feed` RSS/Atom route in `flaskr/blog.py`  
**External services:** none

---

## Stage 2 — Lead Capture: turning visitors into contacts

**Requirement:** When a visitor submits a contact form, their information should be saved and routed to wherever the client manages leads — without losing the submission if something downstream fails.

**Decision: write to the database first, then call external APIs directly.**

The database write always happens. If the CRM call fails, the lead still exists and can be replayed. This ordering — DB first, external services second — is the pattern that keeps user data safe regardless of what tools are in the integration layer.

Direct API calls are used here because this is a Flask app and a developer is implied. But the right choice in production depends on who owns the system after handoff. If someone non-technical needs to swap the CRM, change the confirmation email, or add a step — without calling a developer — then a native integration (many CRMs have direct connectors for common website platforms) or an automation platform is the better answer. The DB-first principle applies either way; what changes is where the integration logic lives.

**New code:** `flaskr/leads.py`, `flaskr/templates/leads/`  
**External services:** CRM API (e.g. HubSpot), email (e.g. Resend) — called directly from Flask

---

## Stage 3 — Gated Content: a human-in-the-loop approval workflow

**Requirement:** Visitors can request access to premium content. The client reviews each request and decides whether to grant access — with the appropriate email sent either way.

**Decision: automation platform (Make) for the approval workflow.**

This is where an automation platform earns its place. The workflow has conditional branching (approve or decline), requires a human decision in the middle, and needs to be modifiable by a non-developer — the client should be able to change the email copy or adjust the approval logic without a code change or deployment.

Implementing this in Flask alone means writing a state machine: request states (`pending`, `approved`, `declined`), routes for the reviewer to trigger transitions, and the right email wired to each outcome. Make handles all of this visually, and hands ongoing ownership to the client.

**New code:** `flaskr/case_studies.py`, `flaskr/templates/case_studies/`  
**External services:** Make — justified here because a non-developer needs to own and modify the workflow

**Limitation:** Case studies are seeded directly in the database — there's no admin UI. Adding or retiring a case study requires a code change. For a real handoff, the client needs either a simple admin interface or a platform with a built-in CMS.

---

## The patterns behind the decisions

The specific tools change. The underlying principles don't.

**Pull before push.** Pull-based integrations (RSS, polling) are simpler and more durable than push-based ones (webhooks) when real-time delivery isn't required. Start with pull; reach for push when you need immediacy or the receiver can't poll.

**DB-first before any external call.** Write to your own datastore before notifying an external service. If the external service is unavailable, your data is still safe.

**Match tool ownership to who will maintain it.** Direct API calls in code are right when a developer owns the integration. An automation platform is right when a non-developer needs to modify the logic after handoff without a deployment.

**External services fail. Design for it.** Timeout, catch exceptions, log failures, have a fallback. Never let a third-party outage surface as a 500 or lose a user's data.

See [docs/design-decisions.md](docs/design-decisions.md) for the full rationale.

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app flaskr init-db
flask --app flaskr run --debug
```

Create a `.env` file — the app runs without external services configured, calls are silently skipped if credentials aren't set:

```
SECRET_KEY=change-me
CRM_API_KEY=
EMAIL_API_KEY=
MAKE_WEBHOOK_CASE_STUDY_REQUEST=
APPROVAL_EMAIL=
```

Visit `http://localhost:5000`. Register an account to create posts and test the forms.

---

## Documentation

| Doc | Contents |
|---|---|
| [docs/design-decisions.md](docs/design-decisions.md) | Architectural principles — the why behind each decision |
| [docs/stage1.md](docs/stage1.md) | Stage 1: RSS/Atom feed implementation |
| [docs/stage2.md](docs/stage2.md) | Stage 2: lead capture, DB-first pattern, direct API calls |
| [docs/stage3.md](docs/stage3.md) | Stage 3: approval workflow, Make setup |
| [docs/free-tier.md](docs/free-tier.md) | Make free plan constraints and workarounds |

---

## Based On

- [Flask Flaskr Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) (BSD-3-Clause)
- Built for the Roux Institute at Northeastern University
