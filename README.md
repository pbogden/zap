# Sentinel Security — Course Demo and Project Prep

This repo serves two related purposes for the Roux Institute web development course and the Sentinel Security client engagement.

---

## Part 1: Flask + Make.com Teaching Demo

*Course material — Weeks 3–4 of the web dev curriculum.*

A teaching demo that extends the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) with real-world automation using [Make.com](https://make.com). The Flaskr tutorial teaches you Flask. This shows what happens after — when a real client needs their app connected to LinkedIn, a CRM, and an approval workflow.

The demo uses the Sentinel Security engagement as its scenario. The patterns it illustrates — not the specific tools — are what carry forward into the actual project.

### Why Make?

The pattern the demo is teaching — draw a boundary between your app and its integrations, 
treat external services as unreliable, write to the DB before firing any webhook — applies 
whether the integration layer is Make, Zapier, direct API calls, or a queue. 

Make is one answer to the problem, not the only one.
Make is most clearly justified for **Stage 3** — a human-in-the-loop approval workflow with 
conditional branching is genuinely awkward to implement in Flask. 
You'd be writing a state machine (requests need states like `pending`, `approved`, `declined`; routes for a reviewer to trigger transitions; and the right email wired to each outcome). Routing it through Make is the simpler choice.

Stages 1 and 2 are more debatable. `requests` is already a dependency, so a Slack notification or HubSpot contact creation is a single `requests.post`. The real question isn't "fewer packages" — it's **who owns the integration logic after handoff**. If the Sentinel team (not a developer) needs to change what happens when a lead comes in — swap the CRM, add an approval step, change the email copy — Make lets them do that without a code change or deploy. If a developer will always make those changes anyway, Make's value shrinks and the added complexity (external service, account, scenario management) becomes harder to justify.

### Three stages

| Stage | Flask adds | Make does | Pattern illustrated |
|---|---|---|---|
| 1 — Blog | `make_webhook.py` + webhook call in `blog.py` + `/feed` RSS | LinkedIn post + Slack notification | Push vs. pull; fire-and-forget |
| 2 — Lead Capture | `leads.py` blueprint | HubSpot contact + confirmation email | DB-first; boundary between app and integrations |
| 3 — Case Studies | `case_studies.py` blueprint | Human-in-the-loop approval workflow | Conditional logic; data ownership |

### The core pattern

All three stages use the same approach: Flask writes to the database first, then fires a webhook to Make. Make handles everything that crosses a system boundary — LinkedIn, HubSpot, email. Flask never imports a LinkedIn or HubSpot SDK.

```
Flask app                Make                    External services
─────────────────────────────────────────────────────────────────
POST /webhook  ──────►  Custom Webhook  ──────►  Slack
  { payload }            Trigger         ├──────►  LinkedIn
                                         └──────►  HubSpot / Email
```

The `make_webhook.py` utility is fire-and-forget: 5-second timeout, catches all exceptions, returns a bool. The app never crashes because Make is unreachable.

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

**Limitation:** The case study list is seeded directly in the DB. There's no admin UI, so adding or retiring a case study requires a code change. For a real handoff, the client needs either a simple admin interface or a platform with a built-in CMS.

### Why these patterns matter regardless of stack

The Flask demo is simple enough that the patterns are visible. But they apply in any stack:

- **DB-first before any external call** — whether you're in Flask, Next.js, or anything else, write to your own datastore before notifying an external service
- **The app owns data and UX; external services own integrations** — this boundary holds whether the "app" is Flask, Webflow, or Next.js, and whether the integration layer is Make, Zapier, or direct API calls
- **Treat external services as unreliable** — timeout, catch exceptions, log failures, have a fallback

See [docs/design-decisions.md](docs/design-decisions.md) for the full rationale with historical and modern context.

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your Make webhook URLs (the app runs fine without them — webhook calls are silently skipped if a URL isn't set):

```
SECRET_KEY=change-me
MAKE_WEBHOOK_BLOG_POST=
MAKE_WEBHOOK_LEAD_CAPTURE=
MAKE_WEBHOOK_CASE_STUDY_REQUEST=
SENTINEL_REVIEW_EMAIL=
```

```bash
flask --app flaskr init-db
flask --app flaskr run --debug
```

Visit `http://localhost:5000`. Register an account to create posts and test the forms.

---

## Part 2: Sentinel Security Project Preparation

*Active — engagement begins May 1, 2026.*

The Roux Institute is building a modernized website for Sentinel Security under SOW No. 26345. A two-student team will design, develop, and launch the site by July 15, 2026.

**The actual deliverable is not a Flask app.** The platform is likely Next.js + Sanity, with Zapier for the case study approval workflow. The Flask demo is background — the project orientation document is what matters now.

### Start here for the project

[docs/project-orientation.md](docs/project-orientation.md) — platform decision, integration approach, open questions to resolve at the April 30 kickoff.

### Key decisions still open

- **Platform:** Next.js + Sanity vs. Webflow — confirm during discovery. The Flask demo exposes a real constraint: without a CMS, the client can't add blog posts, update case studies, or change page copy without a developer. Both Sanity and Webflow solve this; plain Next.js without a CMS does not.
- **CRM:** No CRM in place yet; new hire joining end of April will drive this decision
- **Who owns the site post-handoff:** The new hire, not Stacy — get them to the kickoff

### Project documentation

| Doc | Contents |
|---|---|
| [docs/project-orientation.md](docs/project-orientation.md) | Platform decision, integration approach, open questions — read this first |
| [docs/sow.pdf](docs/sow.pdf) | Statement of Work — 10-week engagement, May 1–July 15, 2026 |

---

## Course Demo Documentation

| Doc | Contents |
|---|---|
| [docs/design-decisions.md](docs/design-decisions.md) | Architectural principles behind the demo — patterns worth carrying into any project |
| [docs/sow-mapping.md](docs/sow-mapping.md) | How each demo stage maps to the Sentinel Security SOW |
| [docs/stage1.md](docs/stage1.md) | Stage 1 Make setup: webhook + RSS alternate approach |
| [docs/stage2.md](docs/stage2.md) | Stage 2 Make setup: lead capture → HubSpot + email |
| [docs/stage3.md](docs/stage3.md) | Stage 3 Make setup: approval workflow |
| [docs/free-tier.md](docs/free-tier.md) | Make free plan constraints and workarounds |

---

## Based On

- [Flask Flaskr Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) (BSD-3-Clause)
- [Make.com](https://make.com) for automation scenarios
- Built for the Roux Institute at Northeastern University
