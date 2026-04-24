# Stage 2 — Lead Capture: Turning Visitors into Contacts

## Functional requirement

When a visitor submits a contact form, their information should be saved and routed to wherever the client manages leads — without losing the submission if something downstream fails.

## Why direct API calls — not an automation platform

An automation platform (Make, Zapier) would handle this without writing integration code. So why not use one here?

The honest answer: for this integration, it doesn't add value. The logic is simple — save a contact, send an email — and a developer owns the code. Adding an automation platform in the middle introduces an external service dependency, an account to manage, and a failure point, without giving the client anything they couldn't get from a well-written API call.

The rule of thumb: use an automation platform when a non-developer needs to own and modify the integration after handoff. Use direct API calls when a developer owns it and the logic is stable. Lead capture is stable logic. Stage 3 is where the rule tips the other way.

The one thing that *does* need special treatment here: the ordering of operations.

---

## The DB-first pattern

Write to your own database before calling any external service. Always.

```python
# 1. Save to database — this always happens
db.execute(
    'INSERT INTO lead (name, email, company, message) VALUES (?, ?, ?, ?)',
    (name, email, company, message)
)
db.commit()
lead_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

# 2. Call external services — these may fail
crm_ok = create_crm_contact(name, email, company, message)
email_ok = send_confirmation_email(name, email)

# 3. Record what happened
db.execute(
    'UPDATE lead SET crm_synced = ?, confirmation_sent = ? WHERE id = ?',
    (crm_ok, email_ok, lead_id)
)
db.commit()
```

If the CRM call fails, the lead still exists in the database. The `crm_synced` column is a record of what happened — not a guarantee. A failed sync can be retried later by querying for rows where `crm_synced = 0`.

This ordering — local write first, external calls second — is a foundation of resilient system design. It applies regardless of whether you're calling a CRM, an automation platform, or anything else.

---

## What Flask adds

**`flaskr/leads.py`** — a new blueprint with:
- `GET /contact` — renders the contact form
- `POST /contact` — validates input, writes to DB, calls external services, redirects

**`flaskr/templates/leads/`** — contact form template

**`flaskr/schema.sql`** — `lead` table with `crm_synced` and `confirmation_sent` columns

---

## The external API calls

### CRM contact creation

Most CRMs have a REST API for creating contacts. The pattern is the same regardless of which CRM the client uses:

```python
import requests

def create_crm_contact(name, email, company, message):
    try:
        response = requests.post(
            'https://api.crm-provider.com/contacts',
            headers={'Authorization': f'Bearer {current_app.config["CRM_API_KEY"]}'},
            json={'email': email, 'name': name, 'company': company},
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'CRM error: {e}')
        return False
```

The 5-second timeout and caught exception mean a slow or unavailable CRM never holds up the user's HTTP request or returns a 500.

### Confirmation email

A transactional email service (Resend, SendGrid, Postmark) sends the confirmation to the visitor. Same pattern — one POST, timeout, catch exceptions, return bool.

```python
def send_confirmation_email(name, email):
    try:
        response = requests.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {current_app.config["EMAIL_API_KEY"]}'},
            json={
                'from': 'hello@yourcompany.com',
                'to': email,
                'subject': 'We received your message',
                'text': f'Hi {name},\n\nThanks for reaching out. We\'ll be in touch soon.'
            },
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Email error: {e}')
        return False
```

---

## Flow

```
Visitor submits contact form
        │
        ▼
Flask validates input
        │
        ▼
DB write — always succeeds (local)          ← lead is never lost
        │
        ├──► CRM API — may fail             ← crm_synced = 0 or 1
        │
        └──► Email API — may fail           ← confirmation_sent = 0 or 1
```

---

## Discussion points

**What if both external calls fail?**
The lead is still in the database. The `crm_synced = 0` rows are a replay queue — a cron job or manual query can retry them later. This is the outbox pattern: your system of record is local; external services are downstream consumers.

**What if you want real-time reliability?**
For high-volume or mission-critical integrations, move the external calls off the request path entirely — write to the DB, enqueue a job (Celery, RQ, or a simple queue table), and let a worker process the queue asynchronously with retries. Flask returns immediately; the user never waits for the CRM.

**When would you use Make or Zapier instead?**
If the client's marketing team needs to change what happens when a lead comes in — swap the CRM, add a Slack notification, change the email copy — without involving a developer. When the integration logic is client-owned, an automation platform is the right tool. See Stage 3.
