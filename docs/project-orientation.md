# Project Orientation: Framer + Make.com

This document is for the student team building Sentinel Security's website, and for anyone
coming into the project without prior experience with Framer or Make.com. It explains what
these tools are, how they fit together, and where things can go wrong.

---

## What you're building

A modernized marketing website for a security consulting firm. The site needs to do four
things that a basic static site can't:

1. **Publish blog posts** that flow automatically to LinkedIn
2. **Capture leads** from a contact form and route them to a CRM (HubSpot or equivalent)
3. **Gate case study access** — visitors request access, Sentinel Security reviews and approves
4. **Host video** with a client-accessible archive

You'll build this in **Framer**, using **Make.com** to handle the integrations. This
document explains what that means in practice.

---

## Framer: the frontend, CMS, and host in one

Framer is a visual web development tool. If you've built React apps before, the mental model
is: Framer is a React app where you work visually instead of writing JSX by hand. Under the
hood it compiles to React. You can write custom code components in TypeScript/React when the
visual editor isn't enough.

What Framer handles for you:
- Page layout and responsive design
- A CMS for structured content (blog posts, case studies, team members)
- Hosting and CDN — you publish directly from Framer, no deployment pipeline
- Form components that can send data to external services via webhook

What Framer does **not** handle:
- Business logic or server-side processing
- Persistent storage of form submissions (leads, access requests)
- Sending emails, posting to LinkedIn, or updating a CRM

That second list is where Make comes in.

---

## Make.com: visual integration plumbing

Make.com is a workflow automation platform. Think of it as a visual programming environment
where each "module" is a pre-built connector to an external service — LinkedIn, HubSpot,
Slack, Gmail, and hundreds of others. You connect modules in a sequence to build a
**scenario**: when X happens, do Y, then Z.

A scenario is triggered by an event. In this project, the trigger will almost always be a
**webhook** — an HTTP POST that Framer sends to Make when a form is submitted or a post is
published. Make receives the payload, runs the scenario, and does whatever you've configured:
create a HubSpot contact, send a confirmation email, post to LinkedIn.

For a developer: Make is where you'd otherwise write glue code calling third-party APIs.
You're not writing code, but you're making the same decisions — which fields to map, what
to do on failure, what order operations run in.

Make has a free tier with significant constraints. See `docs/free-tier.md` for details.

---

## Where the boundary sits

The cleanest way to think about this project:

> **Framer owns the UI and the user experience. Make owns everything that crosses a system
> boundary.**

Framer handles what the visitor sees and does. Make handles what happens in the background
after they act. The connection point between them is a webhook URL — Framer sends, Make
receives.

```
Visitor fills out contact form
        ↓
Framer validates and submits
        ↓
Webhook POST → Make scenario
        ↓
Make creates HubSpot contact + sends confirmation email
```

This boundary matters for a practical reason: **when requirements change, it determines
what has to change with them.** If Sentinel Security switches from HubSpot to Salesforce,
that's a Make reconfiguration — it doesn't touch Framer. If they want to change the form
fields, that's a Framer change — it doesn't touch Make (as long as the field names in the
webhook payload stay consistent).

---

## Three things that matter at the boundary

### 1. Where does the data live?

Framer's CMS stores content — blog posts, case studies, page copy. But it does **not**
persistently store form submissions. When a visitor fills out the lead capture form, that
data goes to Make via webhook. If Make is down or misconfigured, and you haven't set up a
fallback (a Google Sheet, an Airtable, anything), that lead is gone.

**The question to answer early:** Where is the system of record for leads and case study
requests? HubSpot is the likely answer for leads. For case study requests, you may need a
simple spreadsheet or Airtable as a backstop, because the approval workflow in Make depends
on having somewhere to store the pending request.

### 2. Make can fail. The site should still work.

Make is an external service your project doesn't control. It can be slow, down for
maintenance, or misconfigured. If a visitor submits the contact form and Make is
unreachable, what happens? If the answer is "they get an error page and their submission is
lost," that's a problem.

Framer's native form handling gives you some protection — it can show a success message
optimistically before the webhook fires. But you should understand what actually happens to
the data if the downstream Make scenario fails, and make sure there's a recovery path.

### 3. Push and pull are both useful

There are two ways to connect Framer to an external platform:

**Push (webhook):** Framer initiates — when something happens, it immediately sends data to
Make. This is what the lead form and case study request use. It's fast and event-driven, but
it requires Make to be listening.

**Pull (RSS or polling):** The external platform polls Framer on a schedule. An RSS feed at
a predictable URL is the simplest version of this. Newsletter platforms (Mailchimp,
Buttondown, Substack) can drive a blog-to-email campaign by polling an RSS feed directly —
no Make scenario required.

For the blog/LinkedIn integration, both approaches are worth considering. A webhook to Make
is immediate but requires a working scenario. An RSS feed is simpler, more durable, and
compatible with tools Sentinel Security might already use.

---

## Open questions to resolve in discovery (Weeks 1-2)

These are decisions that will shape the technical build. Get answers before you start
designing scenarios.

- **CRM:** HubSpot, Salesforce, or something else? This determines which Make modules you
  use for lead capture.
- **Video hosting:** Not yet decided. Options include Vimeo, Wistia, or a cloud storage
  solution. The choice affects how the client-accessible archive works and who pays for it
  (Sentinel Security covers recurring costs per the SOW).
- **Case study gating:** Framer has some access control options, but they're limited. The
  approval workflow (visitor requests → Sentinel reviews → access granted) may require a
  third-party tool or a creative workaround. Worth prototyping early.
- **LinkedIn posting:** Make's LinkedIn integration has constraints around personal vs.
  company page posting. See `docs/free-tier.md`.

---

## Further reading

| Topic | Resource |
|---|---|
| Framer CMS and components | [Framer documentation](https://www.framer.com/docs/) |
| Make.com scenarios and webhooks | [Make documentation](https://www.make.com/en/help) |
| Three-stage architecture (Flask reference) | `docs/design-decisions.md` — the conceptual principles transfer even though the stack is different |
| Make free tier constraints | `docs/free-tier.md` |
| SOW | `docs/sow.pdf` |
