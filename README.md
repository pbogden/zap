# Flask + Make.com — Webhook Integration Demo

A teaching demo that extends the [Flask Flaskr tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) with [Make.com](https://make.com) automation. The goal is to make the integration boundary pattern visible: how a web app hands off to external services without coupling to them.

---

### Why Make?

The pattern the demo is teaching — draw a boundary between your app and its integrations,
treat external services as unreliable, write to the DB before firing any webhook — applies
whether the integration layer is Make, Zapier, direct API calls, or a queue.

Make is one answer to the problem, not the only one.
Make is most clearly justified for **Stage 3** — a human-in-the-loop approval workflow with
conditional branching is genuinely awkward to implement in Flask.
You'd be writing a state machine (requests need states like `pending`, `approved`, `declined`; routes for a reviewer to trigger transitions; and the right email wired to each outcome). Routing it through Make is the simpler choice.

Stages 1 and 2 are more debatable. `requests` is already a dependency, so a Slack notification or HubSpot contact creation is a single `requests.post`. The real question isn't "fewer packages" — it's **who owns the integration logic after handoff**. If the client team (not a developer) needs to change what happens when a lead comes in — swap the CRM, add an approval step, change the email copy — Make lets them do that without a code change or deploy. If a developer will always make those changes anyway, Make's value shrinks and the added complexity (external service, account, scenario management) becomes harder to justify.

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

### Stage 1 — Blog + Content Syndication

**Functional requirement:** The client wants blog content to reach readers automatically, without manual distribution steps.

**Why pull, not push:** The simplest answer to this requirement is an RSS/Atom feed — a single route that content distribution tools (Mailchimp, Buttondown, Substack) can poll on a schedule. No webhook, no automation account, no external dependency. If the client doesn't have a newsletter yet, the feed sits dormant and costs nothing. If they do, they point their tool at the URL and it works.

A webhook-based push (notifying LinkedIn, Slack, or a team member on publish) solves a coordination problem — publisher and distributor are different people. For a small team where the same person publishes and shares, it's unnecessary overhead. Start with RSS; add push automation only when the coordination problem actually exists.

**New code:** `/feed` RSS/Atom route in `flaskr/blog.py` — no Make required  
**Make:** not used in this stage

### Stage 2 — Lead Capture → Make → HubSpot + Email
A contact form on the site POSTs to Make via webhook. Make creates a HubSpot contact and sends a confirmation email to the prospect.

**New code:** `flaskr/leads.py`, `flaskr/templates/leads/`  
**Make setup:** [docs/stage2.md](docs/stage2.md) — export blueprint to `make_scenarios/stage2_lead_capture/` once built

### Stage 3 — Case Study Request → Make → Approval Workflow
Visitors can request access to gated case studies. Make routes the request to the reviewer, then conditionally sends the download link or a decline email.

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
APPROVAL_EMAIL=
```

```bash
flask --app flaskr init-db
flask --app flaskr run --debug
```

Visit `http://localhost:5000`. Register an account to create posts and test the forms.

---

## Documentation

| Doc | Contents |
|---|---|
| [docs/design-decisions.md](docs/design-decisions.md) | Architectural principles behind the demo — patterns worth carrying into any project |
| [docs/stage1.md](docs/stage1.md) | Stage 1 Make setup: webhook + RSS alternate approach |
| [docs/stage2.md](docs/stage2.md) | Stage 2 Make setup: lead capture → HubSpot + email |
| [docs/stage3.md](docs/stage3.md) | Stage 3 Make setup: approval workflow |
| [docs/free-tier.md](docs/free-tier.md) | Make free plan constraints and workarounds |
| [framer-demo/](framer-demo/README.md) | Same Stage 2 outcome, zero backend — Framer form fires the same Make scenario |

---

## Based On

- [Flask Flaskr Tutorial](https://flask.palletsprojects.com/en/stable/tutorial/) (BSD-3-Clause)
- [Make.com](https://make.com) for automation scenarios
- Built for the Roux Institute at Northeastern University
