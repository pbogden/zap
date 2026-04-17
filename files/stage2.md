# Stage 2 — Lead Capture → Make → HubSpot + Email

## What This Demonstrates

A visitor fills out the contact form at `/contact`. Flask validates the input,
saves the lead to SQLite, then fires a webhook to Make. Make creates a contact
record in HubSpot and sends a confirmation email to the prospect.

Two things worth emphasizing to students:

1. **The DB write happens before the webhook.** The lead is never lost, even if
   Make is unreachable. The `webhook_fired` column records whether Make was
   notified.

2. **Flask doesn't send email.** Email delivery is entirely Make's
   responsibility. Flask just hands off the data.

---

## The Payload Flask Sends

```json
{
  "name": "Alex Rivera",
  "email": "alex@example.com",
  "company": "Meridian Capital",
  "message": "We're evaluating security vendors for a zero-trust rollout..."
}
```

---

## Building the Make Scenario

### Step 1 — Create and configure the webhook

Same process as Stage 1. Create a new scenario, add a **Custom Webhook** module,
name it `sentinel-lead-capture`, and copy the URL to `.env`:

```
MAKE_WEBHOOK_LEAD_CAPTURE=https://hook.us1.make.com/def456uvw
```

Submit the contact form once to teach Make the payload structure.

### Step 2 — Add a HubSpot module

1. Click **+** after the webhook
2. Search **HubSpot CRM** → **Create/Update a Contact**
3. Connect your HubSpot account
4. Map the fields:
   - **Email:** `{{email}}`
   - **First Name:** *(use a text parser to split `{{name}}` — see note below)*
   - **Company:** `{{company}}`
   - **Lead Source:** `Website`
   - Add a custom property if you want to store the message text

> **Splitting the name field:** Make has a built-in **Text Parser** module
> (Functions > Text > Split). Add it before HubSpot, split `{{name}}` on the
> space character, and use `{{1}}` for first name and `{{2}}` for last name.
> This is a good moment to show students how Make handles data transformation.

### Step 3 — Add an Email module (confirmation to prospect)

1. Click **+** after HubSpot
2. Search **Email** → **Send an Email** (or use **Gmail** if preferred)
3. Configure:
   - **To:** `{{email}}`
   - **Subject:** `We received your message — Sentinel Security`
   - **Content:**
     ```
     Hi {{name}},

     Thanks for reaching out to Sentinel Security. We've received your message
     and a member of our team will follow up within one business day.

     — The Sentinel Security Team
     ```

### Step 4 — (Optional) Add a Slack notification

Add a Slack module after the email step to notify the team of the new lead:

- **Channel:** `#leads`
- **Text:**
  ```
  🔔 New lead: *{{name}}* from {{company}}
  {{email}}
  "{{message}}"
  ```

---

## Design Discussion Points

### Why save to the DB before calling Make?

Draw this on the board:

```
Form submit
    │
    ▼
DB write ──── always succeeds (local)
    │
    ▼
Webhook ──── may fail (network, Make outage, misconfiguration)
    │
    ▼
webhook_fired = 0 or 1
```

If Make is down and `webhook_fired = 0`, you can query your DB later and
replay the missed webhooks. This pattern — local-first, external-second — is
a foundation of resilient system design.

### What if you want real-time reliability?

Introduce the concept of a job queue (Celery, RQ, etc.) for firing webhooks
asynchronously with retries. Make is still in the picture; the difference is
how Flask enqueues the work.

---

## Scenario Flow Diagram

```
Flask (leads.py)
  │
  │  POST { name, email, company, message }
  ▼
Make: Custom Webhook
  │
  ├──► Text Parser: Split name → first / last
  │
  ├──► HubSpot: Create/Update Contact
  │      email, first_name, last_name, company
  │
  ├──► Email: Send confirmation to prospect
  │      "Thanks for reaching out..."
  │
  └──► Slack: Notify #leads channel
         "🔔 New lead: {name} from {company}"
```
