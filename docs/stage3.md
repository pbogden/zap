# Stage 3 — Gated Content: Human-in-the-Loop Approval

## Functional requirement

Visitors can request access to premium content. The client reviews each request and decides whether to grant access — with the appropriate email sent either way.

## Why Make — not direct API calls

Stage 2 used direct API calls because the logic was simple, stable, and developer-owned. This stage tips the other way.

The approval workflow has three properties that make an automation platform the right choice:

1. **Conditional branching.** The outcome depends on a human decision — approve or decline — with different emails wired to each path.

2. **Human-in-the-loop.** Execution pauses while a person makes a decision. This isn't a standard request/response cycle.

3. **Non-developer ownership.** The client needs to be able to modify this workflow after handoff — change the email copy, adjust who gets notified, add a step — without a code change or deployment.

Building this in Flask alone means writing a state machine: request states (`pending`, `approved`, `declined`), routes for a reviewer to trigger transitions, and the right email wired to each outcome. That's significant infrastructure for what is fundamentally a business process. Make collapses it to a 10-minute scenario that the client can maintain themselves.

That's when an automation platform earns its place.

---

## What Flask adds

**`flaskr/case_studies.py`** — a new blueprint with:
- `GET /case-studies` — lists available case studies
- `POST /case-studies/<id>/request` — validates input, writes request to DB, fires webhook to Make

**`flaskr/templates/case_studies/`** — list and request form templates

**`flaskr/schema.sql`** — `case_study` and `case_study_request` tables; case studies are seeded directly

**`flaskr/make_webhook.py`** — fire-and-forget webhook utility (reused from the original Flaskr extension)

**Limitation:** There's no admin UI for managing case studies. Adding or retiring one requires a direct database change. For a real handoff, the client needs either a simple admin interface or a platform with a built-in CMS.

---

## The payload Flask sends

```json
{
  "request_id": 7,
  "case_study_id": 2,
  "case_study_title": "Incident Response: Manufacturing Plant Ransomware",
  "case_study_industry": "Manufacturing",
  "requester_name": "Jordan Kim",
  "requester_email": "jordan@example.com",
  "requester_company": "Cascade Industrial",
  "file_url": "https://example.com/case-studies/manufacturing-ransomware.pdf"
}
```

DB write happens before the webhook fires. The request exists even if Make is unreachable.

---

## Building the Make scenario

This stage uses 3 Make scenarios (request handler + approve + decline), which exceeds the free plan's 2-scenario limit. For an instructor demo, deactivate a Stage 1 or Stage 2 scenario before activating the Stage 3 ones. See [free-tier.md](free-tier.md) for the full swap sequence.

### Step 1 — Create the webhook trigger

Create a new scenario, add a **Custom Webhook** module, name it `case-study-request`, and add the URL to `.env`:

```
MAKE_WEBHOOK_CASE_STUDY_REQUEST=https://hook.us1.make.com/abc123
```

Submit a test request to teach Make the payload structure.

### Step 2 — Create approve and decline webhooks

The approval buttons in the email will each point to a Make webhook URL. Create two additional webhooks now:
- `case-study-approve` — triggered when the reviewer clicks Approve
- `case-study-decline` — triggered when the reviewer clicks Decline

Copy both URLs — you'll embed them in the approval email in the next step.

### Step 3 — Send the approval email to the reviewer

After the webhook trigger, add an **Email** module:

- **To:** your `APPROVAL_EMAIL` from `.env`
- **Subject:** `Case Study Request: {{case_study_title}} — {{requester_name}}`
- **Content (HTML):**

```html
<p>New case study request:</p>
<ul>
  <li><strong>Case Study:</strong> {{case_study_title}}</li>
  <li><strong>Industry:</strong> {{case_study_industry}}</li>
  <li><strong>Requester:</strong> {{requester_name}}, {{requester_company}}</li>
  <li><strong>Email:</strong> {{requester_email}}</li>
</ul>
<p>
  <a href="https://hook.us1.make.com/YOUR_APPROVE_URL?request_id={{request_id}}&email={{requester_email}}&title={{case_study_title}}&file_url={{file_url}}"
     style="background:#1a1a2e;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;">
    Approve
  </a>
  &nbsp;&nbsp;
  <a href="https://hook.us1.make.com/YOUR_DECLINE_URL?request_id={{request_id}}&email={{requester_email}}&title={{case_study_title}}"
     style="background:#c00;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;">
    Decline
  </a>
</p>
```

The data needed downstream (email, file URL, title) is passed as query parameters on the button URLs. Make extracts them automatically when those webhooks fire.

### Step 4 — Build the Approve scenario

Create a new scenario triggered by `case-study-approve`. Add an **Email** module:

- **To:** `{{email}}`
- **Subject:** `Your case study request has been approved`
- **Content:**
  ```
  Hi,

  Your request for "{{title}}" has been approved.

  Download it here: {{file_url}}

  This link is for your use only.
  ```

### Step 5 — Build the Decline scenario

Create a new scenario triggered by `case-study-decline`. Add an **Email** module:

- **To:** `{{email}}`
- **Subject:** `Re: Your case study request`
- **Content:**
  ```
  Hi,

  Thank you for your interest in "{{title}}."

  We're not able to share this particular case study at this time.
  We'd be happy to discuss your needs directly — please use our contact form.
  ```

---

## Flow

```
Flask (case_studies.py)
  │
  │  DB write — request saved as 'pending'
  │  POST { request_id, requester_*, case_study_*, file_url }
  ▼
Make Scenario A: Custom Webhook
  │
  └──► Email to reviewer
         [Approve] → hits case-study-approve?email=...&file_url=...
         [Decline] → hits case-study-decline?email=...&title=...


Reviewer clicks Approve
  │
  ▼
Make Scenario B: Custom Webhook (case-study-approve)
  │
  └──► Email to requester: download link


Reviewer clicks Decline
  │
  ▼
Make Scenario C: Custom Webhook (case-study-decline)
  │
  └──► Email to requester: polite decline
```

---

## Discussion points

**What would this cost to build natively in Flask?**
- Async job queue (Celery or RQ) to pause execution until the review happens
- Token-based approval URLs with expiry so links can't be shared or reused
- Email sending with Flask-Mail or similar
- Status tracking in the DB with a reviewer UI to see pending requests

Make collapses all of that to three scenarios the client can modify themselves. For a business process that will change over time, that's the right tradeoff.

**The `request_id` in the payload**
`request_id` is echoed back through the approve/decline URLs. This allows you to update the `case_study_request.status` column in the DB when a decision is made — but only if you add a Flask endpoint that Make calls to confirm the outcome. This is a natural extension exercise: add a `/internal/requests/<id>/status` endpoint and update the row from `pending` to `approved` or `declined`.

**When would you move away from Make?**
If the workflow grows complex enough that Make's visual canvas becomes harder to reason about than code — deeply nested conditionals, many branches, tight latency requirements — it's time to bring it back into the codebase. The same DB-first pattern from Stage 2 applies: write to the DB, enqueue the job, process asynchronously.
