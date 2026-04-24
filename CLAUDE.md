# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A **Flask + Make.com teaching demo** built for the Roux Institute at Northeastern University web development course. It extends the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) with real-world automation using [Make.com](https://make.com).

The demo uses the Sentinel Security client engagement as its scenario — the three stages map to real SOW deliverables — but the repo is course material, not the project deliverable. The actual Sentinel Security website will be built separately in Next.js + Sanity (or Webflow), starting May 1, 2026.

## Two Documents, Two Audiences

**README.md** — the Flask demo. Course material for Weeks 3–4. Covers the webhook pattern, the three stages, and why these patterns matter regardless of stack.

**docs/project-orientation.md** — the Sentinel Security engagement. Active project prep for the student team starting May 1. Covers platform decision (Next.js + Sanity recommended), integration approach, and open questions to resolve at the April 30 kickoff.

Don't conflate them. The Flask demo teaches patterns. The project orientation drives decisions.

## Engagement Context

The Sentinel Security project (SOW No. 26345) is a 10-week engagement — May 1 to July 15, 2026 — in which a two-student Roux Institute team builds a modernized marketing website. Key facts:

- Platform: Next.js + Sanity is the current recommendation; Webflow is the fallback
- CRM: not decided yet — a new hire joining end of April will drive this
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
├── blog.py              # Stage 1: post CRUD + webhook call + /feed RSS
├── leads.py             # Stage 2: lead capture form
├── case_studies.py      # Stage 3: gated case study requests
├── make_webhook.py      # Shared fire-and-forget webhook utility
└── templates/
make_scenarios/          # Make blueprint JSON exports + setup guides
docs/                    # Stage walkthroughs + architecture docs + project orientation
```

## Development Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app flaskr init-db
flask --app flaskr run --debug
```

The app runs without Make webhook URLs configured — calls are silently skipped if URLs aren't set.

## The Core Webhook Pattern

All stages use `make_webhook.fire_webhook(event_type, payload)`:
- Maps `event_type` to `MAKE_WEBHOOK_{EVENT_TYPE}` in app config
- Silently skips if no URL is configured
- 5-second timeout, catches all exceptions, returns `bool`
- Never lets a Make failure surface as a 500 or lose user data

**DB-first in Stages 2 and 3:** Always write to SQLite before firing the webhook. The `webhook_fired` column records whether Make was notified — leads and requests exist even if Make is down.

## Key Design Principles

See `docs/design-decisions.md` for full rationale with sources.

- **DB-first before any external call** — write to your own datastore before notifying an external service
- **The app owns data and UX; external services own integrations** — Flask never imports a LinkedIn or HubSpot SDK
- **Push vs. pull** — Stage 1 demonstrates both: webhook (immediate) and RSS `/feed` (polled)
- **Treat external services as unreliable** — timeout, catch exceptions, log failures

## When Make Is and Isn't Justified

Make is most clearly justified for **Stage 3** — a human-in-the-loop approval workflow with conditional branching is genuinely awkward to implement in Flask alone.

Stages 1 and 2 are more debatable. The real question is who owns the integration logic after handoff. If a non-developer needs to change what happens when a lead comes in, Make lets them do that without a code change. If a developer will always make those changes anyway, Make adds complexity without clear benefit.

For the actual Sentinel Security project: native Webflow/Next.js integrations first, Zapier for the approval workflow, Make only if something specific requires it.

## Documentation

| File | Contents |
|---|---|
| `docs/design-decisions.md` | Architectural principles — the why behind each pattern, with sources |
| `docs/project-orientation.md` | Sentinel Security project prep — platform decision, open questions, kickoff prep |
| `docs/sow-mapping.md` | How each demo stage maps to the SOW deliverables |
| `docs/stage1.md` | Stage 1 Make setup walkthrough |
| `docs/stage2.md` | Stage 2 Make setup walkthrough |
| `docs/stage3.md` | Stage 3 Make setup walkthrough |
| `docs/free-tier.md` | Make free plan constraints and workarounds |
| `docs/sow.pdf` | Sentinel Security Statement of Work |
| `ee.md` | Pre-kickoff meeting notes |
