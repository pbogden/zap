# Project Orientation: Platform, Framer, and Make.com

This document is for the student team building Sentinel Security's website, and for anyone
coming into the project without prior experience with the tools involved. It explains what
the platform options are, how Framer and Make.com fit together, and where things can go
wrong.

---

## What you're building

A modernized marketing website for a security consulting firm. The site needs to do four
things that a basic static site can't:

1. **Convert LinkedIn visitors** — prospective clients discover Sentinel Security on LinkedIn and click through; the website needs to be good enough that they don't immediately leave
2. **Capture leads** from a contact form and route them to a CRM (HubSpot or equivalent)
3. **Gate case study access** — visitors request access, Sentinel Security reviews and approves
4. **Host video** with a client-accessible archive
5. **Support content marketing** — a blog gives visitors something substantive to read and a reason to return; it also gives Sentinel Security material to share manually on LinkedIn

After launch, **Nikki and Stacy at Sentinel Security will manage the site themselves** —
adding blog posts, updating case studies, editing page copy — without developer help and
without technical skills. That requirement shapes the platform choice more than anything
else.

---

## The platform decision

The SOW names Framer as the default platform but leaves the door open for an alternative to
be chosen during discovery. This is a real decision worth making carefully, because the
existing Framer site is in poor shape and neither Nikki nor Stacy has the technical
familiarity to maintain it. Staying on Framer is not a given.

The realistic options are:

**Framer**
A visual web development tool built on React. Strong for design-led builds; the CMS works
but the content editing experience for non-technical users is not its strength. The existing
site is on Framer, but that's not a compelling reason to stay — the site needs to be
rebuilt regardless.

**Webflow**
The closest alternative to Framer, with a significantly better CMS and content editor.
Non-technical users can add blog posts, update pages, and manage collections without
touching the visual editor. The integration story is similar to Framer — Make.com connects
to Webflow via webhooks. Widely used for exactly this kind of professional marketing site.
Webflow is the most likely alternative if Framer is ruled out.

**WordPress**
The most accessible content editing experience of any platform — Nikki and Stacy may
already be familiar with it. Plugin ecosystem handles most integration needs, though it
often means more maintenance overhead. Worth considering if content ownership is the
primary concern and the team is comfortable with the tradeoffs.

**The key question to answer in discovery:** Can Nikki and Stacy comfortably manage content
on whatever platform you choose? Ask them to try adding a blog post or updating a page
during the discovery phase — before you commit to a platform — and watch what happens.

For the rest of this document, the integration patterns apply regardless of which platform
you choose. The boundary between the site and Make.com looks the same whether the site is
built in Framer, Webflow, or something else.

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

For the blog, this is worth thinking through carefully — see the LinkedIn question below.

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
- **LinkedIn — clarify the actual goal:** The SOW mentions "LinkedIn connectivity" but it's
  worth understanding exactly what Sentinel Security needs before building anything. The most
  likely scenario is that prospective clients find Sentinel Security on LinkedIn and click
  through to the website — meaning the website is the problem to solve, not the LinkedIn
  presence. Automatically pushing blog posts to LinkedIn is a separate feature with real
  complexity (Make's LinkedIn integration has constraints around personal vs. company pages)
  and questionable value if Sentinel Security is already posting manually. Ask Nikki in
  discovery: are people finding you on LinkedIn but leaving the website? Or do you want to
  post more content to LinkedIn with less effort? Those are different problems.

---

## Further reading

| Topic | Resource |
|---|---|
| Framer CMS and components | [Framer documentation](https://www.framer.com/docs/) |
| Make.com scenarios and webhooks | [Make documentation](https://www.make.com/en/help) |
| Three-stage architecture (Flask reference) | `docs/design-decisions.md` — the conceptual principles transfer even though the stack is different |
| Make free tier constraints | `docs/free-tier.md` |
| SOW | `docs/sow.pdf` |
