# Sentinel Security Demo — Flaskr + Make.com

A teaching demo that extends the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) with real-world automation using [Make.com](https://make.com). Each stage maps directly to a deliverable in the [Sentinel Security SOW](docs/sow-mapping.md).

---

## Why This Exists

The Flaskr tutorial teaches you Flask. This repo shows you what happens *after* — when a real client needs their app connected to LinkedIn, a CRM, and an approval workflow. The three stages below are the gap between "I finished the tutorial" and "this is production-ready."

| Flaskr feature | SOW deliverable | Extended by |
|---|---|---|
| Blog (create/read/edit) | Blog/newsletter section | Stage 1 |
| Auth (register/login) | Gated access | Stage 3 |
| Forms + validation | Lead capture | Stage 2 |
| SQLite DB | Data foundation | All stages |

---

## Make.com Free Plan

This demo runs on Make's free plan for an instructor-led walkthrough. The only
constraint is a 2-active-scenario limit — Stage 3 requires 3 scenarios, so you'll
swap them in and out as you move through the stages. See [docs/free-tier.md](docs/free-tier.md)
for the full rundown, including the LinkedIn workaround and how to handle RSS polling.

---

## Stages

### Stage 1 — Blog Post → Make → Slack + LinkedIn
When a post is published, Flask fires a webhook to Make. Make cross-posts to LinkedIn and sends a Slack notification. `blog.py` also serves a `/feed` RSS route as a pull-model alternative.

**New code:** `flaskr/make_webhook.py`, one webhook call and `/feed` RSS route in `flaskr/blog.py`  
**Make setup:** [docs/stage1.md](docs/stage1.md) — export blueprint to `make_scenarios/stage1_blog_notify/` once built

### Stage 2 — Lead Capture → Make → HubSpot + Email
A contact form on the site POSTs to Make via webhook. Make creates a HubSpot contact and sends a confirmation email to the prospect.

**New code:** `flaskr/leads.py`, `flaskr/templates/leads/`  
**Make setup:** [docs/stage2.md](docs/stage2.md) — export blueprint to `make_scenarios/stage2_lead_capture/` once built

### Stage 3 — Case Study Request → Make → Approval Workflow
Visitors can request access to gated case studies. Make routes the request to the Sentinel team for review, then conditionally sends the download link or a decline email.

**New code:** `flaskr/case_studies.py`, `flaskr/templates/case_studies/`  
**Make setup:** [docs/stage3.md](docs/stage3.md) — export blueprint to `make_scenarios/stage3_case_study_approval/` once built

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/sentinel-flaskr-demo.git
cd sentinel-flaskr-demo
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file and add your Make webhook URLs. The app runs fine without them — webhook calls are silently skipped if a URL isn't set.

```bash
SECRET_KEY=change-me
MAKE_WEBHOOK_BLOG_POST=
MAKE_WEBHOOK_LEAD_CAPTURE=
MAKE_WEBHOOK_CASE_STUDY_REQUEST=
SENTINEL_REVIEW_EMAIL=
```

See the [Environment Variables](#environment-variables) table below for details on each.

### 3. Initialize the database and run

```bash
flask --app flaskr init-db
flask --app flaskr run --debug
```

Visit `http://localhost:5000`. Register an account to create posts and test the forms.

---

## Project Structure

```
sentinel-flaskr-demo/
├── flaskr/
│   ├── __init__.py          # App factory — registers all blueprints
│   ├── db.py                # Database connection helpers
│   ├── schema.sql           # Tables: user, post, lead, case_study, case_study_request
│   ├── auth.py              # Register / login / logout (Flaskr, unchanged)
│   ├── blog.py              # Post CRUD + Stage 1 webhook call + /feed RSS
│   ├── leads.py             # Stage 2: lead capture form
│   ├── case_studies.py      # Stage 3: gated case study requests
│   ├── make_webhook.py      # Shared webhook utility used by all stages
│   └── templates/
│       ├── base.html
│       ├── auth/
│       ├── blog/
│       ├── leads/
│       └── case_studies/
├── make_scenarios/
│   └── README.md            # Blueprint export/import instructions (blueprints added once built)
├── docs/
│   ├── design-decisions.md  # Architectural principles behind the demo
│   ├── free-tier.md         # Make free plan constraints and workarounds
│   ├── sow-mapping.md       # How each stage maps to the Sentinel SOW
│   ├── stage1.md            # Stage 1 Make setup walkthrough
│   ├── stage2.md            # Stage 2 Make setup walkthrough
│   └── stage3.md            # Stage 3 Make setup walkthrough
├── framer-demo/             # Same Stage 2 outcome, zero backend
└── requirements.txt
```

---

## Documentation

The `docs/` folder contains both the Make setup walkthroughs and the
architectural context for the decisions behind the demo.

| Doc | Contents |
|---|---|
| [docs/design-decisions.md](docs/design-decisions.md) | Architectural principles behind the demo — the concepts worth carrying into the next project |
| [docs/sow-mapping.md](docs/sow-mapping.md) | How each stage maps to the Sentinel Security SOW |
| [docs/stage1.md](docs/stage1.md) | Stage 1 Make setup: webhook + RSS alternate approach |
| [docs/stage2.md](docs/stage2.md) | Stage 2 Make setup: lead capture → HubSpot + email |
| [docs/stage3.md](docs/stage3.md) | Stage 3 Make setup: approval workflow |
| [framer-demo/](framer-demo/README.md) | Same Stage 2 outcome, zero backend — Framer form fires the same Make scenario |

---

## Environment Variables

| Variable | Stage | Description |
|---|---|---|
| `SECRET_KEY` | All | Flask secret key |
| `MAKE_WEBHOOK_BLOG_POST` | 1 | Webhook URL for new blog posts |
| `MAKE_WEBHOOK_LEAD_CAPTURE` | 2 | Webhook URL for lead form submissions |
| `MAKE_WEBHOOK_CASE_STUDY_REQUEST` | 3 | Webhook URL for case study access requests |
| `SENTINEL_REVIEW_EMAIL` | 3 | Email address for case study approval notifications |

---

## The Webhook Pattern

All three stages use the same approach. Flask sends a `POST` request with a JSON payload to a Make webhook URL. Make receives it and routes it to external services. Your Flask app doesn't need to know anything about Slack, HubSpot, or email — it just fires and forgets.

```
Flask app                Make                    External services
---------                ----                    -----------------
POST /webhook  ──────►  Custom Webhook  ──────►  Slack
  { payload }            Trigger         ├──────►  LinkedIn
                                         └──────►  HubSpot / Email
```

The utility function in `make_webhook.py` handles this for all three stages:

```python
fire_webhook("BLOG_POST", {
    "title": title,
    "author": g.user["username"],
    "url": url_for("blog.detail", id=post_id, _external=True),
})
```

---

## Based On

- [Flask Flaskr Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) (BSD-3-Clause)
- [Make.com](https://make.com) for automation scenarios
- Built for the Roux Institute at Northeastern University
