# Project Orientation: Platform and Integration

This document is for the student team building Sentinel Security's website, and for anyone
coming into the project without prior experience with the tools involved. It explains what
the platform options are, how the site and Make.com fit together, and where things can go
wrong.

*Updated April 21, 2026 based on pre-kickoff meeting notes and current platform research.*

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

**Who manages the site after handoff:** A new hire joining at end of April will likely own
the site and the CRM strategy going forward. This is an important person to meet at or
before the kickoff — they may have strong opinions about platform and tooling, and building
something they can't or won't use would be a problem. Stacy is the current operational
contact and will handle technical access and approvals in the meantime.

---

## The platform decision

The SOW names Framer as the default but leaves the door open for an alternative. Based on
the pre-kickoff meeting, Framer is effectively ruled out: Stacy reports that the existing
site was locked down by whoever built it, she couldn't modify sections or keep responsive
versions in sync, and the site has deteriorated as a result. These are not user errors —
they reflect real limitations in how Framer was used here.

The site needs to be rebuilt regardless. The question is what to rebuild it in.

**Webflow** — the recommended choice for this engagement.
The closest alternative to Framer, with a significantly better CMS and content editor.
Non-technical users can add blog posts, update pages, and manage structured content without
touching the visual editor. A React developer can be productive in Webflow within a day or
two; the learning curve is UI conventions, not new concepts.

The Make.com integration is native and well-supported — Make has an official Webflow
integration with 40 modules covering forms, CMS, and site events. One gotcha: creating or
updating a CMS item through Make does not automatically publish it to the live site; you
need an explicit publish step in your scenario.

For analytics, Webflow now offers a built-in privacy-friendly analytics add-on ($9/mo) that
requires no third-party setup — relevant given that Sentinel Security currently has no
visibility into site traffic. The CMS plan ($23/mo billed annually) supports 2,000 CMS
items, which is more than sufficient.

**Ghost** — worth knowing about, but a narrower fit.
Ghost is a publishing platform built specifically for content-first sites, with newsletter
and email list functionality built in. The editor is excellent, Ghost Pro handles hosting,
and pricing starts at $15/mo. Ghost 6.0 (August 2025) added ActivityPub syndication for
decentralized social distribution. The limitation is that it's a publishing platform first —
custom page layouts, multiple content types (case studies, team bios, video archive), and
marketing-focused design are more constrained than Webflow. If the blog and newsletter
become the dominant use case, Ghost is worth a second look. For a full marketing site with
multiple page types, Webflow is the better fit.

**Framer** — ruled out based on Stacy's direct experience.
The existing site deteriorated because Framer builds can become unmanageable without ongoing
developer involvement. Not the right tool for a team that needs to own the site after
handoff.

**WordPress** — not recommended for this project.
Still the most widely deployed CMS on the web, but increasingly the wrong choice for new
professional builds. For a student team that knows React, it means learning a PHP ecosystem
without transferable skills. More importantly: a WordPress site with unpatched plugins is a
real security liability — a particularly awkward choice for a security consulting firm.

**Next.js + headless CMS** — the most technically transferable option, but not right for
this engagement.
You know React and Vite. Next.js is the step up most professional React teams take —
server-side rendering, file-based routing, API routes, deployed on Vercel. Paired with a
headless CMS like Sanity, non-technical users get a clean editing interface while you
control the frontend. The design principles in `docs/design-decisions.md` apply directly
here in a way they don't in a visual tool.

The honest tradeoff: Next.js has its own mental model (server vs. client components, the
App Router, data fetching patterns), and the ecosystem moves fast enough that documentation
goes stale quickly. Add a headless CMS on top and you've doubled the learning surface. With
10 weeks and a real client deadline, learning Next.js risks consuming the first few weeks on
infrastructure rather than Sentinel Security's actual site. Next.js is the right choice for
a course project with more runway and no client deadline.

**Recommendation:** Webflow for this engagement. Confirm it with Stacy during discovery —
ask her to try editing a page and adding a blog post before committing.

---

## Automation: do you actually need Make?

The Flask teaching demo in this repo uses Make.com extensively, but that's a pedagogical
choice, not a project requirement. For the actual Sentinel Security site, the honest
answer is: start with native integrations and only add an automation layer when you
need one.

**What Webflow handles natively, no automation tool required:**
- Form submissions are stored in the Webflow dashboard and trigger email notifications
  out of the box — leads aren't lost even if nothing else is configured
- HubSpot has an official certified app in the Webflow Marketplace that maps form fields
  directly to HubSpot contacts with no code and no third-party service
- Mailchimp and several other email list tools have similar native integrations

**When you do need an automation layer:**
The case study approval workflow is the one feature that genuinely benefits from automation
— a visitor requests access, Sentinel Security receives a notification, reviews the request,
and a conditional email goes out based on their decision. That multi-step conditional flow
is where a tool like Make or Zapier earns its keep.

**Make vs. Zapier:**
If you do need an automation layer, Zapier is the better choice for this project. It's
simpler for beginners, has guided setup, and connects to 8,000+ apps. Make is more powerful
for complex multi-branch scenarios but has a steeper learning curve and a free tier that's
easy to exhaust. For a student team new to both tools, Zapier gets you to a working scenario
faster. The conceptual patterns — webhooks, payloads, conditional logic — are the same in
either tool.

**Recommended approach:**
1. Launch with native Webflow form handling — submissions go to the dashboard, email
   notifications go to Stacy or the new hire
2. Add the HubSpot native integration once the CRM decision is made
3. Use Zapier only for the case study approval workflow, which needs conditional logic that
   native integrations can't handle
4. Revisit Make if scenarios grow complex enough to justify it

---

## Where the boundary sits

The cleanest way to think about this project:

> **The site owns the UI and the user experience. External services own everything that
> crosses a system boundary.**

The site handles what the visitor sees and does. Everything else — CRM updates, emails,
notifications, approval workflows — happens outside it. How that handoff works depends on
which integration approach you use:

```
Visitor fills out contact form
        ↓
Webflow stores submission + sends email notification   ← native, no extra tool
        ↓ (if HubSpot chosen)
HubSpot native app syncs contact to CRM               ← native, no extra tool
        ↓ (for case study approval)
Zapier scenario: notify → review → conditional email  ← automation layer needed here
```

This boundary matters for a practical reason: **when requirements change, it determines
what has to change with them.** If Sentinel Security switches CRMs, that's an integration
change — it doesn't touch the site. If they want to change the form fields, that's a site
change — it doesn't touch the integrations (as long as field names stay consistent).

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

- **CRM and new hire:** No CRM in place yet. A new hire joining end of April will own the
  CRM strategy and likely the site itself. Try to have them at the kickoff on April 30 or
  loop them in immediately after. Don't finalize the lead capture integration until they've
  weighed in — building to the wrong CRM wastes time. A Google Sheet via Make is a
  reasonable temporary backstop while the decision is pending.

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

- **Analytics:** Not using any. If you go with Webflow, the built-in Analyze add-on ($9/mo)
  is the simplest path — privacy-friendly, no third-party setup, cookieless. Otherwise
  Plausible is a clean lightweight option. Either way this is a quick win and was explicitly
  called out as something they want.

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
