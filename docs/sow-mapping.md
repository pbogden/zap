# SOW Mapping — Flaskr to Sentinel Security

This document shows how each part of the demo maps to a specific deliverable
in the [Sentinel Security Statement of Work](../docs/sow.pdf).

---

## The Core Argument

The Flaskr tutorial teaches you to build a working web app. But the SOW describes
something more: an app that is *connected* — to LinkedIn, to a CRM, to an internal
approval workflow. That connection layer is what Make provides.

```
Flaskr tutorial        →   This repo          →   Sentinel SOW
──────────────────────────────────────────────────────────────────
Blog (CRUD)            →   + webhook          →   Blog/newsletter + LinkedIn
Forms + validation     →   + Make routing     →   Lead capture → CRM
Auth (login/register)  →   + gated requests   →   Case study access control
SQLite DB              →   + leads/requests   →   Data foundation
```

---

## Stage-by-Stage Mapping

### Stage 1 — Blog → LinkedIn + Slack

**SOW language (Phase 2):**
> *"Build a blog/newsletter section with LinkedIn integration, allowing content
> to flow between the website and Sentinel Security's LinkedIn presence."*

**What Flaskr already gives you:** A fully working blog with create, read,
update, delete, and authentication.

**What we add:** A single `fire_webhook()` call in `blog.py` after a post is
saved. Make picks it up and handles the distribution — LinkedIn API, Slack
API — without any of that code living in Flask.

**Why this matters for the SOW:** The client didn't ask you to become a LinkedIn
API expert. They asked for content to flow between systems. Make is how you
deliver that without building and maintaining OAuth flows for every platform.

---

### Stage 2 — Lead Capture → HubSpot + Email

**SOW language (Phase 2):**
> *"Build a lead capture form integrated with Sentinel Security's CRM or
> preferred lead management system (e.g., HubSpot, Salesforce, or equivalent)."*

**What Flaskr already gives you:** Form handling, validation, flash messages,
database writes.

**What we add:** `leads.py` — a new blueprint that saves the submission to the
DB first, then fires a webhook to Make. Make creates a HubSpot contact and sends
a confirmation email.

**The important design decision:** The DB write and the webhook are independent.
If Make is unreachable, the lead is still saved. This is a real production
pattern — your system of record is always local; external integrations are
best-effort.

---

### Stage 3 — Case Study Requests → Approval Workflow

**SOW language (Phase 2):**
> *"Implement a case study showcase with or without a gated submission portal
> that captures prospective client information and allows Sentinel Security to
> vet inquiries before releasing materials."*

**What Flaskr already gives you:** Auth, templates, database.

**What we add:** `case_studies.py` — a blueprint that lists case study summaries
(public), accepts access requests (gated by form), and fires a webhook that
triggers a human-in-the-loop approval flow in Make.

**Why Make, not Flask?** The approval workflow is asynchronous and involves a
human decision. Implementing this in Flask would require background jobs, email
sending, token-based approval links, and state management. Make handles all of
it with a few modules and no additional infrastructure.

---

## What's Out of Scope (and Why)

The SOW lists several features as explicitly out of scope for this engagement:

| Out-of-scope item | Why it matters |
|---|---|
| Client portal with authenticated login | Would require per-client auth, roles, and a dashboard — significant scope |
| Event calendar with registration | Third-party tools (Eventbrite, Luma) handle this better |
| Ongoing content creation | Client responsibility per SOW Section 4 |
| Long-term hosting / maintenance | Separate engagement |

Notice that none of the out-of-scope items are things Make could easily solve.
They're scope decisions, not integration decisions. This is a useful distinction:
Make helps you *connect* things; it doesn't help you *decide* what to build.

---

## The Pattern This Demo Teaches

Every Make integration in this repo follows the same shape:

1. **Flask does the web work** — forms, validation, DB writes, responses
2. **Flask fires a webhook** — one function call, fire-and-forget
3. **Make does the integration work** — external APIs, email, approval loops

The seam between Flask and Make is always the webhook. Understanding where to
draw that line — what belongs in your app vs. what belongs in an automation
platform — is one of the core skills this project is designed to develop.
