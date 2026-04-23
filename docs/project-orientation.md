# Project Orientation: Platform and Integration

This document is for the student team building Sentinel Security's website, and for anyone
coming into the project without prior experience with the tools involved.

*Updated April 23, 2026 based on pre-kickoff meeting notes, current platform research, and
a reassessment of the platform decision in the context of AI-assisted development.*

---

## How you'll work: Claude Code

You'll be building with Claude Code — Anthropic's AI coding assistant — as a core part of
your workflow. This changes the platform decision significantly, so read the platform section
carefully before assuming no-code tools are the safer choice.

Claude Code can scaffold a Next.js app, set up a headless CMS, write integration code,
debug across the full stack, and explain framework concepts as you encounter them. The
learning curve for an unfamiliar framework is no longer measured in weeks — it's measured
in hours. Every obstacle is a conversation.

This doesn't mean architecture decisions are free. You still need to think clearly about
what you're building, make deliberate choices about content structure, and ensure that what
gets handed off to Stacy and the new hire is something they can actually use. But the
execution risks that historically made "junior team, unfamiliar stack, tight deadline" a
concerning combination are largely gone.

---

## What you're building

A modernized marketing website for a security consulting firm. The current site is broken
and effectively inert — no analytics, no lead capture, no blog, no CRM. Sentinel Security
doesn't know if anyone visits the site. Prospective clients who find them on LinkedIn or at
conferences land on a site that doesn't represent the quality of their work.

The site needs to:

1. **Convert LinkedIn visitors** — the website needs to be good enough that people who
   click through from LinkedIn don't immediately leave
2. **Capture leads** from a contact form and route them to a CRM
3. **Gate case study access** — visitors request access, Sentinel Security reviews and approves
4. **Support a blog** — gives visitors something substantive to read; gives Sentinel Security
   material to share on LinkedIn
5. **Host video** — they do webinars and want a place to archive them
6. **Analytics** — basic traffic visibility; they currently have none

**What's not in place yet:** No CRM. No blog. No email marketing. No intake form. No
videos. Content exists in a brochure but hasn't been organized for the web.

**Who manages the site after handoff:** A new hire joining at end of April will likely own
the site and the CRM strategy. This is an important person to involve at or before the
April 30 kickoff — building something they can't or won't use is a real risk. Stacy is the
current operational contact and handles technical access in the meantime.

---

## The platform decision

Framer is ruled out — Stacy confirmed the existing site was locked down by whoever built
it, she couldn't modify sections or keep responsive versions in sync, and it deteriorated
as a result. The site needs to be rebuilt regardless of platform.

The real choice is between two approaches:

---

### Option A: Next.js + Sanity — recommended

**Next.js** is the framework most professional React teams use. You know React and Vite;
Next.js adds server-side rendering, file-based routing, and API routes. Deployed on Vercel,
the hosting story is as simple as any no-code tool. With Claude Code, the learning curve is
not a meaningful obstacle — you'll be productive within a day.

**Sanity** is a headless CMS that gives Stacy and the new hire a clean, well-designed
editing interface for managing blog posts, case studies, bios, and page content — without
touching code. Sanity Studio is fully customizable and ships with real-time collaboration,
version history, and as of 2025, an MCP server that lets Claude Code interact with your
content directly.

**Why this is the right choice with Claude Code:**
- Every obstacle is a code problem — and code problems are exactly where Claude Code excels
- The approval workflow, the gating logic, the CRM integration — all writable, testable,
  version-controlled code rather than visual scenario editors
- The team builds transferable skills on a stack they'll use professionally
- When Sentinel Security needs changes after handoff, any developer can work on it

**The one real risk:** The client editing experience depends on how well you set up Sanity
Studio. If content modeling gets deprioritized under deadline pressure, you hand off a site
nobody can update. Do this first, not last — get Stacy into Sanity early and confirm she
can add a blog post before you build anything else.

**Pricing:** Vercel free tier covers hosting for a site this size. Sanity free tier covers
up to 3 users and 10GB — sufficient for this project. Growth plan is $15/mo if needed.

---

### Option B: Webflow — viable fallback

If the team decides the client editing experience is the dominant constraint and wants it
solved out of the box, Webflow is the right fallback. The CMS editor is genuinely good for
non-technical users, the Make.com and HubSpot integrations are native, and a React
developer can be productive within a day or two.

The tradeoff: you're working within Webflow's constraints rather than writing code. When
you hit a wall — and the approval workflow will test those limits — Claude Code can't help
you the way it can with a codebase. Webflow's visual canvas is outside its reach.

**CMS plan:** $23/mo billed annually, 2,000 CMS items, sufficient for this project.
Built-in analytics add-on: $9/mo, privacy-friendly, no third-party setup needed.

---

### Ghost, WordPress — not recommended

**Ghost** is a publishing platform with a built-in newsletter. Strong editor, good for
content-first sites. Too constrained for a full marketing site with multiple content types,
custom page layouts, and gated access.

**WordPress** is the wrong choice for a new professional build in 2026. PHP ecosystem with
no transferable value for a React team. Unpatched plugin vulnerabilities are a real security
liability — particularly embarrassing for a security consulting firm.

---

## Integration: how much automation do you actually need?

Less than you might think. The Flask teaching demo uses Make.com throughout, but that's a
pedagogical choice. For this project, start with the simplest thing that works.

**What the platform handles natively:**
- Webflow stores form submissions in its dashboard and sends email notifications out of the box
- If you go with Next.js, a form submission handler is a few lines of code with Claude Code
- HubSpot has official native integrations with both Webflow and Next.js — no third-party
  tool required for basic lead capture once the CRM decision is made

**Where automation genuinely helps:**
The case study approval workflow — visitor requests access, Sentinel Security reviews,
conditional email goes out — is the one flow that benefits from an automation layer.
For this, Zapier is simpler than Make for a team new to both. The conceptual patterns are
the same; Zapier has better documentation and a lower learning curve.

With Next.js, the approval workflow is also just code — an API route, a database record,
an email sent via Resend or similar. Claude Code can write this. Whether you use Zapier or
code it directly is a judgment call about what Sentinel Security can maintain after handoff.

**Recommended approach regardless of platform:**
1. Native form handling first — submissions stored, email notifications sent, no dependencies
2. HubSpot native integration once the CRM decision is made
3. Zapier (or code) for the case study approval workflow only
4. Don't add Make unless something specific requires it

---

## Where the boundary sits

> **The site owns the UI and the user experience. External services own everything that
> crosses a system boundary.**

The site handles what the visitor sees and does. CRM updates, emails, notifications, and
approval workflows happen outside it. The handoff point is either a native integration or
a webhook.

```
Visitor fills out contact form
        ↓
Site stores submission + sends email notification     ← always works, no dependencies
        ↓ (once CRM decided)
HubSpot native integration syncs contact              ← native, no extra tool
        ↓ (case study approval)
Zapier or API route: notify → review → conditional email
```

If Sentinel Security switches CRMs later, that's an integration change — it doesn't touch
the site. If they want to change form fields, that's a site change — it doesn't touch the
integrations.

---

## Open questions to resolve in discovery (Weeks 1–2)

- **Platform:** Confirm Next.js + Sanity or Webflow. Get Stacy into the content editor of
  whichever you choose before committing — watch her add a blog post.

- **New hire and CRM:** The new hire joining end of April will likely own the site and the
  CRM. Get them to the April 30 kickoff or loop them in immediately after. Don't finalize
  the lead capture integration until they've weighed in.

- **LinkedIn — clarify the actual goal:** The SOW mentions "LinkedIn connectivity" but the
  real goal is probably just a website good enough that LinkedIn visitors don't leave. Ask
  Nikki: are people finding you on LinkedIn but leaving the website? That's a design
  problem. Or do you want to automate posting to LinkedIn? That's a separate feature with
  real complexity. Confirm before building anything.

- **Video:** No videos exist yet. They want to archive webinars from Teams/Zoom. Build the
  infrastructure, but don't expect content at launch. Vimeo or Wistia are the likely
  options; Sentinel Security covers recurring costs per the SOW.

- **Analytics:** Plausible is a clean, privacy-friendly option that works with any platform.
  If you go Webflow, their built-in Analyze add-on ($9/mo) is simpler. Either way, set this
  up at launch — it was explicitly called out as something they want.

- **Privacy policy:** They have a draft. Needs to appear clearly on the site.

- **Case study gating:** The most technically complex feature. With Next.js this is custom
  code (session tokens, access records, conditional rendering). With Webflow it requires a
  third-party tool or creative workaround. Prototype it early regardless of platform.

- **Content:** Primary source is a company brochure. Bios coming for new hires joining end
  of April. Provide content templates and structure early — Sentinel Security is responsible
  for copy per the SOW, but they need to know what to write.

- **Design reference:** Nikki mentioned Emergent Risk International as a site they like.
  Review it before the April 30 kickoff.

---

## Further reading

| Topic | Resource |
|---|---|
| Next.js documentation | [nextjs.org/docs](https://nextjs.org/docs) |
| Sanity getting started | [sanity.io/docs](https://www.sanity.io/docs) |
| Webflow University | [university.webflow.com](https://university.webflow.com) |
| Zapier getting started | [zapier.com/learn](https://zapier.com/learn) |
| Integration principles (Flask reference) | `docs/design-decisions.md` — principles transfer regardless of platform |
| SOW | `docs/sow.pdf` |
| Pre-kickoff meeting notes | `ee.md` |
