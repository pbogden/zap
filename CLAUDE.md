# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A **teaching demo** that extends the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) with [Make.com](https://make.com) automation. Built for the Roux Institute at Northeastern University as part of the Sentinel Security engagement.

The repo is currently **documentation and reference code only** — the actual Flask app has not been scaffolded yet. The `docs/` folder contains the reference Python files (`blog.py`, `leads.py`, `case_studies.py`, `make_webhook.py`, `schema.sql`) that will become the app.

## Intended Project Structure (once scaffolded)

```
sentinel-flaskr-demo/
├── flaskr/
│   ├── __init__.py          # App factory — registers all blueprints
│   ├── db.py                # Database connection helpers
│   ├── schema.sql           # Tables: user, post, lead, case_study, case_study_request
│   ├── auth.py              # Register / login / logout (standard Flaskr)
│   ├── blog.py              # Post CRUD + Stage 1 webhook call + /feed RSS
│   ├── leads.py             # Stage 2: lead capture form → Make → HubSpot
│   ├── case_studies.py      # Stage 3: gated case study requests → approval workflow
│   ├── make_webhook.py      # Shared fire-and-forget webhook utility
│   └── templates/
├── make_scenarios/          # Make blueprint JSON exports + setup guides
├── docs/                    # Stage walkthroughs + reference code + architecture docs
├── .env.example
└── requirements.txt
```

## Development Commands (once scaffolded)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add Make webhook URLs
flask --app flaskr init-db
flask --app flaskr run --debug
```

Visit `http://localhost:5000`. Register an account to create posts and exercise the forms.

## Three-Stage Architecture

Each stage adds one Flask blueprint and one Make scenario:

| Stage | Flask adds | Make does |
|---|---|---|
| 1 — Blog | `fire_webhook()` in `blog.py` + `/feed` RSS route | LinkedIn post + Slack notification |
| 2 — Lead Capture | `leads.py` blueprint (`/contact`) | HubSpot contact creation + confirmation email |
| 3 — Case Studies | `case_studies.py` blueprint (`/case-studies`) | Human-in-the-loop approval → conditional email |

## The Core Webhook Pattern

All stages use `make_webhook.fire_webhook(event_type, payload)` — a fire-and-forget utility that:
- Maps `event_type` (e.g. `"BLOG_POST"`) to `MAKE_WEBHOOK_{EVENT_TYPE}` in app config
- Silently skips if no URL is configured (app runs fine without Make)
- Has a 5-second timeout, catches all exceptions, returns `bool`
- Never lets a Make failure surface as a 500 or lose the user's data

**DB-first pattern in Stages 2 and 3:** Always write to SQLite before firing the webhook. The `webhook_fired` column records whether Make was notified — leads and requests exist even if Make is down.

## Environment Variables

| Variable | Stage | Purpose |
|---|---|---|
| `SECRET_KEY` | All | Flask session secret |
| `MAKE_WEBHOOK_BLOG_POST` | 1 | Webhook URL for new posts |
| `MAKE_WEBHOOK_LEAD_CAPTURE` | 2 | Webhook URL for lead form submissions |
| `MAKE_WEBHOOK_CASE_STUDY_REQUEST` | 3 | Webhook URL for case study access requests |
| `SENTINEL_REVIEW_EMAIL` | 3 | Email for approval notifications |

## Key Design Principles (see `docs/design-decisions.md`)

- **Flask owns data and UX. Make owns integrations.** Flask never imports a LinkedIn or HubSpot SDK.
- **Your system of record never depends on an external service.** DB write always precedes webhook.
- **Push vs. pull:** Stage 1 demonstrates both — webhook (immediate) and RSS `/feed` (polled). RSS is compatible with Mailchimp/Substack/Buttondown without any Make scenario.
- **Make is a dependency.** Treat it like one: timeout, catch exceptions, log failures.

## Documentation in `docs/`

| File | Contents |
|---|---|
| `design-decisions.md` | Architectural principles — the "why" behind each pattern |
| `sow-mapping.md` | How each stage maps to the Sentinel Security SOW deliverables |
| `free-tier.md` | Make free plan constraints: 2-scenario limit, LinkedIn workaround, RSS "Run once" trick |
| `stage1.md` | Make scenario walkthrough: Custom Webhook → Slack + LinkedIn |
| `stage2.md` | Make scenario walkthrough: lead capture → HubSpot + email |
| `stage3.md` | Make scenario walkthrough: approval workflow |
| `blog.py` | Reference implementation for Stage 1 |
| `leads.py` | Reference implementation for Stage 2 |
| `case_studies.py` | Reference implementation for Stage 3 |
| `make_webhook.py` | Reference implementation for the shared webhook utility |
| `schema.sql` | Full schema with seed data for the three demo case studies |
