# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A **Flask teaching demo** built for the Roux Institute at Northeastern University web development course. It extends the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) with three stages of real-world integration, each driven by a functional requirement from a small startup client.

The demo is not tied to a specific client or platform. Each stage asks: what's the simplest approach that meets the requirement? The decision-making process is the lesson, not the tools.

## Two Documents, Two Audiences

**README.md** — the Flask demo. Course material for Weeks 3–4. Each stage starts with a functional requirement and justifies the technical decision.

**docs/project-orientation.md** — the Sentinel Security engagement. Active project prep for the student team starting May 1, 2026. Platform decision (Next.js + Sanity recommended), integration approach, open questions for the April 30 kickoff.

Don't conflate them. The demo teaches patterns. The orientation drives decisions for a specific real project.

## Sentinel Security Engagement Context

The Sentinel Security project (SOW No. 26345) is a 10-week engagement — May 1 to July 15, 2026 — in which a two-student Roux Institute team builds a modernized marketing website. Key facts:

- Platform: Next.js + Sanity is the current recommendation; Webflow is the fallback
- CRM: not decided — a new hire joining end of April will drive this
- The new hire will likely own the site post-handoff; get them to the April 30 kickoff
- Framer (the existing platform) is ruled out — Stacy confirmed it became unmanageable
- The site is effectively inert: no analytics, no blog, no lead capture, no CRM

The SOW is at `docs/sow.pdf`. Pre-kickoff meeting notes are in `ee.md`.

## Flask Demo Structure

```
flaskr/
├── __init__.py          # App factory — registers all blueprints
├── db.py                # Database connection helpers
├── schema.sql           # Tables: user, post, lead, case_study, case_study_request
├── auth.py              # Register / login / logout (standard Flaskr, unchanged)
├── blog.py              # Stage 1: post CRUD + /feed RSS/Atom route
├── leads.py             # Stage 2: lead capture form + direct API calls
├── case_studies.py      # Stage 3: gated content requests + Make webhook
├── make_webhook.py      # Fire-and-forget webhook utility (Stage 3 only)
└── templates/
make_scenarios/          # Make blueprint JSON exports (Stage 3 only)
docs/                    # Stage walkthroughs + architecture docs + project orientation
```

## Development Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app flaskr init-db
flask --app flaskr run --debug
```

The app runs without external services configured — calls are silently skipped if credentials aren't set.

## The Three Stages

Each stage is driven by a functional requirement. The technology follows the requirement.

**Stage 1 — Blog: reaching an audience**
Requirement: content should reach subscribers automatically without manual distribution.
Decision: RSS/Atom feed. Pull is simpler than push when real-time delivery isn't required and the publisher and distributor are the same person. No external service needed.

**Stage 2 — Lead Capture: turning visitors into contacts**
Requirement: form submissions should be saved and routed to the CRM without losing data if something downstream fails.
Decision: DB-first, then direct API calls. Write to SQLite before calling the CRM or sending email. A developer owns this code; an automation platform adds complexity without adding value here.

**Stage 3 — Gated Content: human-in-the-loop approval**
Requirement: visitors request access to premium content; the client reviews each request and approves or declines.
Decision: Make automation platform. The workflow has conditional branching and requires a non-developer to own and modify it after handoff — the client needs to change email copy or approval logic without a deployment. This is where Make is justified.

## Key Design Principles

See `docs/design-decisions.md` for full rationale with sources.

- **Pull before push** — pull-based integrations are simpler and more durable when real-time delivery isn't required
- **DB-first before any external call** — write to your own datastore before notifying an external service
- **Match tool ownership to who will maintain it** — code when a developer owns it; automation platform when a non-developer does
- **External services fail; design for it** — timeout, catch exceptions, log failures, never lose user data

## When Make Is and Isn't Justified

Make appears in Stage 3 only. The reasoning:

- **Stage 1:** No automation needed. RSS is pull-based and self-contained.
- **Stage 2:** Direct API calls are sufficient. Logic is simple, developer-owned, better in code.
- **Stage 3:** Make is justified. Conditional branching, human-in-the-loop, non-developer ownership after handoff.

The general principle: use an automation platform when a non-developer needs to modify the integration logic without a code deployment. Use direct API calls or native integrations when a developer owns the integration.

## Documentation

| File | Contents |
|---|---|
| `docs/design-decisions.md` | Architectural principles — the why behind each pattern, with sources |
| `docs/project-orientation.md` | Sentinel Security project prep — platform decision, open questions, kickoff prep |
| `docs/stage1.md` | Stage 1: RSS/Atom feed implementation |
| `docs/stage2.md` | Stage 2: lead capture, DB-first pattern, direct API calls |
| `docs/stage3.md` | Stage 3: approval workflow, Make setup |
| `docs/free-tier.md` | Make free plan constraints and workarounds |
| `docs/sow.pdf` | Sentinel Security Statement of Work |
| `ee.md` | Pre-kickoff meeting notes |
