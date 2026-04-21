# Project Orientation: Platform and Integration

This document is for the student team building Sentinel Security's website, and for anyone
coming into the project without prior experience with the tools involved. It explains what
the platform options are, how the site and Make.com fit together, and where things can go
wrong.

*Updated April 21, 2026 based on pre-kickoff meeting notes.*

---

## What you're building

A modernized marketing website for a security consulting firm. The current site is broken
and effectively inert — no analytics, no lead capture, no blog, no CRM. Sentinel Security
doesn't know if anyone visits the site. Prospective clients who find them on LinkedIn or at
conferences land on a site that doesn't represent the quality of their work.

The site needs to do several things a basic static site can't:

1. **Convert LinkedIn visitors** — prospective clients discover Sentinel Security on LinkedIn
   and click through; the website needs to be good enough that they don't immediately leave
2. **Capture leads** from a contact form and route them to a CRM
3. **Gate case study access** — visitors request access, Sentinel Security reviews and approves
4. **Support a blog** — gives visitors something substantive to read and gives Sentinel
   Security material to share on LinkedIn
5. **Host video** — they do webinars and speaking engagements; they want a place to put them
6. **Analytics** — basic traffic visibility; they currently have none

**What's not in place yet:** No CRM. No blog. No email marketing. No intake form. No
videos. The content exists in a brochure and in people's heads, but hasn't been organized
for the web.

**Who manages the site after handoff:** This is an open question. Stacy is the operational
contact and the person most likely to touch the site day-to-day, but she struggled with the
existing Framer site. The platform choice needs to be something she can actually use.

---

## The platform decision

The SOW names Framer as the default but leaves the door open for an alternative. Based on
the pre-kickoff meeting, Framer is effectively ruled out: Stacy reports that the existing
site was locked down by whoever built it, she couldn't modify sections or keep responsive
versions in sync, and the site has deteriorated as a result. These are not user errors —
they reflect real limitations in how Framer was used here.

The site needs to be rebuilt regardless. The question is what to rebuild it in.

**Webflow** — the most likely choice for this engagement.
The closest alternative to Framer, with a significantly better CMS and content editor.
Non-technical users can add blog posts, update pages, and manage structured content without
touching the visual editor. The integration story is the same as Framer — Make.com connects
via webhooks. Widely used for exactly this kind of professional marketing site. A React
developer can be productive in Webflow within a day or two; the learning curve is UI
conventions, not new concepts.

**Framer** — probably not the right choice here.
Strong for design-led builds, but the content editing experience for non-technical users is
not its strength, and the existing site is evidence of how Framer builds can become
unmanageable without developer involvement. Not recommended unless there's a specific reason
to revisit.

**WordPress** — worth considering if content ownership is the dominant concern.
The most accessible content editing experience of any platform. Stacy and Nikki may already
know it. Plugin ecosystem handles most integration needs, though it often means more
maintenance overhead and security surface area.

**Next.js + headless CMS** — the most technically transferable option, but probably not
right for this engagement.
You know React and Vite. Next.js is the step up most professional React teams take —
server-side rendering, file-based routing, API routes, deployed on Vercel. Paired with a
headless CMS like Sanity, non-technical users get a clean editing interface while you
control the frontend. The design principles in `docs/design-decisions.md` apply directly
here in a way they don't in a visual tool.

The honest tradeoff: learning Next.js is harder than learning Webflow. Webflow is a visual
tool — a React developer can be productive within a day or two. Next.js has its own mental
model (server vs. client components, the App Router, data fetching patterns), and the
ecosystem moves fast enough that documentation goes stale quickly. Add a headless CMS on
top and you've doubled the learning surface. With 10 weeks and a real client deadline,
learning Next.js risks consuming the first few weeks on infrastructure rather than
Sentinel Security's actual site. Next.js is the right choice for a course project with more
runway and no client deadline.

**Recommendation:** Webflow for this engagement. Confirm it with Stacy during discovery —
ask her to try editing a page and adding a blog post before committing.

---

## Make.com: visual integration plumbing

Make.com is a workflow automation platform. Think of it as a visual programming environment
where each "module" is a pre-built connector to an external service — LinkedIn, HubSpot,
Slack, Gmail, and hundreds of others. You connect modules in a sequence to build a
**scenario**: when X happens, do Y, then Z.

A scenario is triggered by an event. In this project, the trigger will almost always be a
**webhook** — an HTTP POST that the site sends to Make when a form is submitted. Make
receives the payload, runs the scenario, and does whatever you've configured: create a CRM
contact, send a confirmation email, notify Sentinel Security of a case study request.

For a developer: Make is where you'd otherwise write glue code calling third-party APIs.
You're not writing code, but you're making the same decisions — which fields to map, what
to do on failure, what order operations run in.

Make has a free tier with significant constraints. See `docs/free-tier.md` for details.

---

## Where the boundary sits

The cleanest way to think about this project:

> **The site owns the UI and the user experience. Make owns everything that crosses a system
> boundary.**

The site handles what the visitor sees and does. Make handles what happens in the background
after they act. The connection point between them is a webhook URL — the site sends, Make
receives.

```
Visitor fills out contact form
        ↓
Site validates and submits
        ↓
Webhook POST → Make scenario
        ↓
Make creates CRM contact + sends confirmation email
```

This boundary matters for a practical reason: **when requirements change, it determines
what has to change with them.** If Sentinel Security chooses a CRM now and switches later,
that's a Make reconfiguration — it doesn't touch the site. If they want to change the form
fields, that's a site change — it doesn't touch Make (as long as the field names in the
webhook payload stay consistent).

---

## Three things that matter at the boundary

### 1. Where does the data live?

The site's CMS stores content — blog posts, case studies, page copy. But it does **not**
persistently store form submissions. When a visitor fills out the lead capture form, that
data goes to Make via webhook. If Make is down or misconfigured, and you haven't set up a
fallback (a Google Sheet, an Airtable, anything), that lead is gone.

**The question to answer early:** Where is the system of record for leads and case study
requests? The CRM decision is currently blocked — a new hire joining at end of April will
have input on it. Don't finalize the lead capture integration until that decision is made.
For case study requests, a simple Google Sheet as a backstop is worth setting up regardless
of what CRM they choose.

### 2. Make can fail. The site should still work.

Make is an external service the project doesn't control. It can be slow, down for
maintenance, or misconfigured. If a visitor submits the contact form and Make is
unreachable, what happens? If the answer is "they get an error and their submission is
lost," that's a problem.

Most platforms' native form handling can show a success message optimistically before the
webhook fires. But you should understand what actually happens to the data if the downstream
Make scenario fails, and make sure there's a recovery path.

### 3. Push and pull are both useful

There are two ways to connect the site to an external platform:

**Push (webhook):** The site initiates — when something happens, it immediately sends data
to Make. This is what the lead form and case study request use. Fast and event-driven, but
requires Make to be listening.

**Pull (RSS or polling):** The external platform polls the site on a schedule. Newsletter
platforms (Mailchimp, Buttondown, Substack) can drive a blog-to-email campaign by polling
an RSS feed directly — no Make scenario required. Worth keeping in mind once Sentinel
Security is ready to do email marketing.

---

## Open questions to resolve in discovery (Weeks 1-2)

These are decisions that will shape the technical build. Several are currently blocked on
Sentinel Security decisions.

- **Platform:** Webflow vs. alternatives. Confirm with Stacy by having her try the content
  editing experience before committing.

- **CRM:** No CRM in place yet. A new hire joining end of April will have strategy and
  ideas. Don't build the lead capture integration until this is decided. In the meantime,
  a Google Sheet via Make is a reasonable temporary backstop.

- **LinkedIn — clarify the actual goal:** The SOW mentions "LinkedIn connectivity" but the
  real goal may simply be a website good enough that LinkedIn visitors don't immediately
  leave. Automatically pushing blog posts to LinkedIn is a separate, more complex feature.
  Ask Nikki: are people finding you on LinkedIn but leaving the website? That's a design
  problem. Or do you want to post more content to LinkedIn with less effort? That's an
  automation problem. They're different.

- **Video:** No videos exist yet. They do webinars on Teams/Zoom and want to capture and
  archive them. Build the infrastructure, but don't expect content at launch. Video hosting
  platform TBD — Vimeo and Wistia are the likely options; Sentinel Security covers recurring
  costs per the SOW.

- **Analytics:** Not using any. Adding basic analytics (Plausible or Google Analytics) is a
  quick win and was explicitly called out as something they want.

- **Privacy policy:** They have a draft. It needs to appear clearly on the site.

- **Case study gating:** The approval workflow (visitor requests → Sentinel reviews → access
  granted) is the most technically complex feature. Platform access control options vary
  significantly — worth prototyping early to avoid a late-stage surprise.

- **Content:** A company brochure is the primary source. Bios for core team members are
  coming — new people joining end of April. Content delivery is Sentinel Security's
  responsibility per the SOW, but the team should provide templates and structure early so
  Sentinel Security knows what to write.

- **Design reference:** Nikki mentioned Emergent Risk International as a site they like.
  Worth reviewing before the kickoff meeting on April 30.

---

## Further reading

| Topic | Resource |
|---|---|
| Webflow CMS and integrations | [Webflow University](https://university.webflow.com) |
| Make.com scenarios and webhooks | [Make documentation](https://www.make.com/en/help) |
| Integration principles (Flask reference) | `docs/design-decisions.md` — the conceptual principles transfer regardless of platform |
| Make free tier constraints | `docs/free-tier.md` |
| SOW | `docs/sow.pdf` |
| Pre-kickoff meeting notes | `ee.md` |
