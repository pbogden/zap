# Stage 3 — Case Study Request → Make → Approval Workflow

## What This Demonstrates

This is the most sophisticated stage. When a visitor requests a case study,
Make runs an **asynchronous, human-in-the-loop approval workflow** — something
that would require significant infrastructure to build natively in Flask.

The flow:
1. Flask fires a webhook with the request details
2. Make emails the Sentinel team with Approve / Decline buttons
3. A team member clicks a button
4. Make sends the requester either the download link or a polite decline

Flask's role ends after step 1. The rest is entirely Make.

---

## The Payload Flask Sends

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

---

## Building the Make Scenario

This scenario uses Make's **waiting for a webhook response** pattern, which
pauses execution until an external event (the approval click) resumes it.

### Step 1 — Create the webhook trigger

Same as previous stages. Name it `sentinel-case-study-request` and add the URL to `.env`:

```
MAKE_WEBHOOK_CASE_STUDY_REQUEST=https://hook.us1.make.com/ghi789rst
```

Submit a test case study request to teach Make the payload structure.

### Step 2 — Add a second Custom Webhook (for the approval response)

The approval buttons in the email will each point to a URL. The simplest
approach is to create **two additional webhooks** in Make:
- `sentinel-cs-approve` — triggered when the team clicks Approve
- `sentinel-cs-decline` — triggered when the team clicks Decline

Create these now and copy their URLs. You'll embed them in the approval email.

> **Alternative:** Use Make's built-in **Wait** module to pause the scenario and
> resume on a webhook response. This keeps everything in one scenario but
> requires a Make plan that supports waiting. The two-webhook approach works on
> all plans.

### Step 3 — Send the approval email to the Sentinel team

After the webhook trigger, add an **Email** module:

- **To:** *(your `SENTINEL_REVIEW_EMAIL` from `.env`)*
- **Subject:** `Case Study Request: {{case_study_title}} — {{requester_name}}`
- **Content (HTML):**
  ```html
  <p>A new case study request has come in:</p>
  <ul>
    <li><strong>Case Study:</strong> {{case_study_title}}</li>
    <li><strong>Industry:</strong> {{case_study_industry}}</li>
    <li><strong>Requester:</strong> {{requester_name}}</li>
    <li><strong>Company:</strong> {{requester_company}}</li>
    <li><strong>Email:</strong> {{requester_email}}</li>
  </ul>
  <p>
    <a href="https://hook.us1.make.com/YOUR_APPROVE_WEBHOOK?request_id={{request_id}}&email={{requester_email}}&title={{case_study_title}}&file_url={{file_url}}"
       style="background:#1a1a2e;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;">
      ✅ Approve
    </a>
    &nbsp;&nbsp;
    <a href="https://hook.us1.make.com/YOUR_DECLINE_WEBHOOK?request_id={{request_id}}&email={{requester_email}}&title={{case_study_title}}"
       style="background:#c00;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;">
      ❌ Decline
    </a>
  </p>
  ```

> The data you need downstream (email, file URL, case study title) is passed
> as query parameters on the button URLs. Make extracts them automatically when
> those webhooks are triggered. This is a handy pattern to highlight.

### Step 4 — Build the Approve scenario

Create a new scenario triggered by the `sentinel-cs-approve` webhook.

After the trigger, add an **Email** module:

- **To:** `{{email}}` *(from the query params)*
- **Subject:** `Your Sentinel Security Case Study is Ready`
- **Content:**
  ```
  Hi,

  Great news — your request for "{{title}}" has been approved.

  You can download the full case study here:
  {{file_url}}

  This link is for your use only. Please don't share it publicly.

  — Sentinel Security
  ```

### Step 5 — Build the Decline scenario

Create a new scenario triggered by the `sentinel-cs-decline` webhook.

After the trigger, add an **Email** module:

- **To:** `{{email}}`
- **Subject:** `Re: Your Case Study Request — Sentinel Security`
- **Content:**
  ```
  Hi,

  Thank you for your interest in "{{title}}."

  After reviewing your request, we're not able to share this particular
  case study at this time. We'd be happy to discuss your needs directly —
  please feel free to reach out via our contact page.

  — Sentinel Security
  ```

---

## Design Discussion Points

### Why not just send the link immediately?

This is the SOW's specific requirement: *"allows Sentinel Security to vet
inquiries before releasing materials."* The vetting is a business requirement,
not a technical one. Make makes it implementable without building a whole
admin dashboard.

Ask students: what would this feature cost to build natively in Flask?
- Async job queue (Celery or RQ)
- Token-based approval URLs with expiry
- Email sending (Flask-Mail or similar)
- Status tracking in the DB
- An admin UI to see pending requests

Make collapses all of that to a 10-minute scenario.

### The `request_id` in the payload

Notice that `request_id` is included in the webhook payload and echoed back
through the approval/decline URLs. This allows you to update the
`case_study_request.status` column in your DB — but only if you build a small
Flask endpoint that Make can call to confirm the outcome.

This is a natural extension exercise: add a `/internal/case-study-request/<id>/status`
endpoint that Make can POST to, and update the row from `pending` to `approved`
or `declined`.

---

## Full Flow Diagram

```
Flask (case_studies.py)
  │
  │  POST { request_id, case_study_title, requester_*, file_url }
  ▼
Make Scenario A: Custom Webhook (sentinel-case-study-request)
  │
  └──► Email to Sentinel team
         [✅ Approve] → hits sentinel-cs-approve?email=...&file_url=...
         [❌ Decline] → hits sentinel-cs-decline?email=...&title=...


Team member clicks Approve
  │
  ▼
Make Scenario B: Custom Webhook (sentinel-cs-approve)
  │
  └──► Email to requester: "Your case study is ready — {file_url}"


Team member clicks Decline
  │
  ▼
Make Scenario C: Custom Webhook (sentinel-cs-decline)
  │
  └──► Email to requester: "We're unable to share this at this time..."
```
