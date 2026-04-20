# Flask vs. Framer — A Side-by-Side Comparison

Both demos produce the same outcome: a contact form submission creates a
HubSpot contact and pings Slack. This document maps every step of that
journey in both tools so you can see exactly where they're the same,
where they differ, and what each difference teaches.

---

## The full journey, side by side

| Step | Flask demo | Framer demo |
|---|---|---|
| Form rendered | Jinja template (`leads/index.html`) | Framer canvas (no code) |
| Input validation | Python (`leads.py`) | Client-side only (Framer) |
| Submit handler | `@bp.route("/contact", methods=["POST"])` | Framer's built-in form handler |
| Database write | `INSERT INTO lead ...` (SQLite) | ❌ None |
| Webhook fired | `fire_webhook("LEAD_CAPTURE", {...})` | Framer "Send To → Webhook" setting |
| Payload sent | `{"name": ..., "email": ..., ...}` | `{"name": ..., "email": ..., ...}` |
| Make receives | Custom Webhook trigger | Custom Webhook trigger |
| HubSpot contact | Create/Update Contact module | Create/Update Contact module |
| Slack notification | Create Message module | Create Message module |
| `webhook_fired` recorded | ✅ Yes | ❌ No |
| Failed webhook recoverable | ✅ Yes (query DB, replay) | ❌ No |

Everything from "Webhook fired" downward is identical. The divergence is
entirely in the left side — how the form works and what happens to the data
before it leaves your system.

---

## Where the code is

In the Flask demo, you can read every decision:

```python
# leads.py — the moment the form is submitted

# 1. Validate
if not name:
    error = "Your name is required."

# 2. Write to DB — always happens, regardless of Make
db.execute("INSERT INTO lead (name, email, company, message) VALUES (?, ?, ?, ?)",
           (name, email, company, message))
db.commit()

# 3. Fire webhook — may silently fail
webhook_fired = fire_webhook("LEAD_CAPTURE", {
    "name": name,
    "email": email,
    "company": company,
    "message": message,
})

# 4. Record the outcome
db.execute("UPDATE lead SET webhook_fired = ? WHERE id = ?",
           (1 if webhook_fired else 0, lead_id))
```

In the Framer demo, all of this is replaced by two UI settings:
- Form fields, each with a name and a type
- A webhook URL in the "Send To" panel

There is no equivalent of the DB write or the `webhook_fired` flag. There
is no server-side validation. There is no place to put those things —
Framer is a design and publishing tool, not a backend.

---

## What the Framer version trades away

### 1. Persistence

The Flask demo writes every submission to SQLite before doing anything
else. The lead exists in your system the moment the form is submitted,
regardless of what Make does.

The Framer demo has no storage. If Make's webhook is misconfigured, the
submission is lost. If Make is down, the submission is lost. If the
Framer → Make connection breaks silently, you won't know.

**The question to ask students:** *Is that acceptable for Sentinel's
lead capture form?* The answer depends on how critical each lead is.
For a high-value B2B security firm, probably not. For a low-traffic
portfolio contact form, probably fine.

### 2. Server-side validation

Flask validates in Python — on the server, after the form is submitted,
before anything is stored or sent. A user cannot bypass it by disabling
JavaScript or manipulating the form in browser dev tools.

Framer validates client-side only. A user with browser dev tools can
submit an empty form, a malformed email, or fabricated data.

**The question to ask students:** *For a contact form, does this matter?*
Probably not much — a spammer who submits garbage to a contact form causes
minor annoyance at worst. For a payment form or authentication form, it
would matter enormously.

### 3. Auditability

The Flask demo has a `leads` table. You can query it:

```sql
-- Which leads never reached Make?
SELECT * FROM lead WHERE webhook_fired = 0;

-- How many leads this month?
SELECT COUNT(*) FROM lead
WHERE created >= date('now', 'start of month');
```

The Framer demo has no equivalent. Your only records are in Make's
execution history (retained for 30 days on the free plan) and in
HubSpot (which depends on Make having run successfully).

---

## What the Framer version gains

### 1. Speed of setup

The Framer demo takes about 20 minutes to build and publish. The Flask
demo takes significantly longer — you need a Python environment,
database initialization, and a running server before you can test
anything.

For a client who needs a contact form live by tomorrow, Framer wins.

### 2. Client maintainability

Nikki Rutman at Sentinel Security can log into Framer and update the
form fields, change the page copy, or add a new field without involving
a developer. She cannot do the equivalent in the Flask app without
editing Python.

This is the SOW's requirement: *"Establish a foundation that Sentinel
Security's team can maintain and build on over time."* Framer satisfies
that more directly than Flask does.

### 3. Hosting included

The Framer site is live at a public URL with zero infrastructure
decisions. The Flask app needs a server, a deployment process, and
ongoing maintenance.

---

## The make scenario: why it's identical

Make receives a JSON payload from a webhook URL. It doesn't know or care
whether that payload came from:
- A `requests.post()` call in a Python function
- A Framer form's "Send To" setting
- A Zapier workflow
- A curl command in a terminal

As long as the payload has the fields Make expects — `name`, `email`,
`company`, `message` — the scenario runs identically. This is what
"decoupled" means in practice: the integration layer has no dependency
on the tool that triggers it.

You can demonstrate this directly in class by showing both demos firing
the same Make scenario:

1. Show the Make scenario's execution history after a Flask form submission
2. Show it again after a Framer form submission
3. The two runs are indistinguishable in Make's UI

That's the moment the lesson lands.

---

## When to use each

| Situation | Reach for |
|---|---|
| Client needs site live quickly, will maintain it themselves | Framer |
| Lead data is high-value, zero loss acceptable | Flask |
| You need server-side validation or auth | Flask |
| Client is non-technical, no developer on retainer | Framer |
| You need an audit trail of all submissions | Flask |
| Prototyping or demonstrating to a client before build | Framer |
| Building a foundation for future features (API, portal, etc.) | Flask |

Most real projects start with Framer and graduate to Flask (or a similar
backend) when they hit the limits the table above describes. The Sentinel
SOW is a good example — it starts with a Framer site but the full
requirements (gated case studies, CRM integration, approval workflows)
suggest they'll need more backend capability over time.

---

## The one-sentence summary

Framer and Flask are both valid ways to fire a webhook. The question isn't
which tool fires it better — they're identical from Make's perspective. The
question is what happens *before* the webhook fires: who owns the data,
where it lives, and what happens when things go wrong.
