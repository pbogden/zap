# Web App Integration Demo

claude --resume 6e02bb4c-60a0-4024-87d6-314b77c27773

A teaching demo built on the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/). Each stage adds a feature driven by a real functional requirement from a small startup client. For each requirement, we ask: what's the simplest approach that actually meets the need? The answer isn't always the same tool.

---

## What this demo is — and isn't

**Flask is a developer tool.** Here's how it compares to the realistic alternatives for a client-facing site:

| | Flask | Django + Wagtail | Next.js + Sanity | Webflow |
|---|:---:|:---:|:---:|:---:|
| Non-developer content editing | ✗ | ✓ | ✓ | ✓ |
| No developer for site changes | ✗ | ✗ | ✗ | ✓ |
| AI features added on (chatbot, drafting) | ✓ | ✓ | ✓ | ✗ |
| Vercel AI SDK / Sanity MCP | ✗ | ✗ | ✓ | ✗ |
| AI as the product (Python ecosystem) | — | ✓ | — | ✗ |
| Used in this demo | ✓ | | | |

**AI features added on** — chatbot, AI-assisted drafting, lead qualification layered onto a marketing site. Next.js + Sanity is the strongest choice: the Vercel AI SDK handles AI-enhanced web UIs, and Sanity's MCP server (hosted at `mcp.sanity.io`, auto-configured by Claude Code) lets AI agents query content, manage releases, and patch documents with full schema awareness. If you want an AI that drafts blog posts and saves them to the CMS, that's available now.

**AI as the product** — agents doing substantial reasoning, orchestration, or data processing — is where Python becomes competitive. The Python AI ecosystem (Anthropic SDK, LangChain, LangGraph, LlamaIndex) is significantly more mature than the JavaScript equivalents; the right architecture is a Python AI backend with a React frontend. For that backend: **Django** for complex, stateful AI applications (structure, ORM, admin, data management); **FastAPI** for lightweight, API-first AI backends (async-native, auto-generated docs, what most AI framework examples use).

A few other Python tools worth knowing:

- **Pydantic** — foundational to modern Python. FastAPI is built on it, LangChain uses it, the Anthropic SDK uses it. Structured, validated data objects — Python's answer to TypeScript's type system.
- **Streamlit / Gradio / Chainlit** — rapid Python AI interfaces. Streamlit is general-purpose; Gradio for single-function demos; Chainlit for chat and LLM apps. Any of the three is faster than React for an internal tool or prototype.
- **Modal** — serverless Python infrastructure with GPU access on demand. Pay for compute used. Not always the most cost-effective; some teams prefer RunPod or self-hosted.

**So why use Flask for this demo?** Because Flask is transparent. The patterns — write to your database before calling external services, match your tool choice to who will maintain the integration, design for failure at system boundaries — are visible in a way they aren't in higher-abstraction frameworks. Learn the pattern here; apply it in whatever stack you actually build with.

---

## The client

A small professional services firm — a few people, no dedicated technical staff, growing. They have a website with a blog. They want to reach more clients, capture leads, and share expertise without adding operational overhead.

---

## How to read this demo

Each stage starts with a **functional requirement** — what the client actually needs, in plain language. Then it explains why a particular approach was chosen over alternatives. The decision is the lesson, not just the code.

---

## Handoff

Every decision in this demo is shaped by one question: **who can change this after the project ends?**

Flask always requires a developer — to deploy, update dependencies, or modify an integration when an upstream API changes. For a client with no technical staff, that's a structural constraint the platform can't solve. The better handoff is a platform like Webflow or Next.js + Sanity, where content management doesn't require a developer. Flask is used here because the patterns are easier to see without framework abstractions — but the patterns apply regardless of platform.

The three stages give three different answers to the ownership question:

| Stage | Integration | Who owns it after handoff |
|---|---|---|
| 1 — Blog | RSS/Atom feed | Nobody — configure once, runs indefinitely |
| 2 — Lead capture | Direct API calls | A developer — logic is stable, Flask implies one |
| 3 — Gated content | Make automation | A non-developer — client needs to modify the workflow |

Stage 3 is the one case where Make is justified — not because the logic is complex, but because a non-developer needs to own and modify it. That distinction is the point.

The same question applies to the platform itself — not just the integrations, but who can manage the site day-to-day:

| Platform | Content edits | Code changes |
|---|---|---|
| Flask (this demo) | Developer required | Developer required |
| Django + Wagtail | Non-developer via Wagtail editor | Developer required |
| Next.js + Sanity | Non-developer via Sanity Studio | Developer required |
| Webflow | Non-developer — no code needed | Within Webflow's visual constraints |

Django + Wagtail and Next.js + Sanity both give non-technical staff a content editor while keeping code in developer hands. Webflow goes further — no developer required for day-to-day management, within its canvas constraints. The case for Next.js + Sanity over the Python path: matching it with Python means running Django as an API with a separate React frontend — more moving parts for the same result, and the frontend ecosystem has pulled ahead on the JavaScript side.

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
