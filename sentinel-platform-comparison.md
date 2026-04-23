# Sentinel Security — Platform Comparison
> SOW reference: Statement of Work No. 26345, Northeastern University / Roux Institute × Sentinel Security

---

## Context

The Sentinel Security SOW scopes a 10-week website redesign covering:

- Modern, professional web presence
- Blog/newsletter with LinkedIn integration
- Gated case study access with lead capture
- CRM integration (HubSpot or equivalent)
- Video hosting with client-facing archive
- Foundation Sentinel's team can maintain post-handoff

Five platform options were evaluated: **Next.js + Vercel**, **React + Vite**, **Framer**, and **Webflow**.

---

## Feature Comparison

### SOW Features

| Criterion | Next.js + Vercel | React + Vite | Framer | Webflow |
|-----------|-----------------|--------------|--------|---------|
| Blog + LinkedIn sync | ✅ Headless CMS + custom API route | ⚠️ Needs separate backend + CMS | ⚠️ Built-in CMS, no LinkedIn API | ⚠️ Built-in CMS, no LinkedIn API |
| Gated case studies | ✅ Middleware-level route auth | ⚠️ Possible via separate backend auth | ⚠️ FramerAuth plugin available; paid third-party, not native | ⚠️ Possible via DevLink React component + external backend |
| Lead capture + CRM | ✅ API route → HubSpot SDK | ⚠️ Separate backend API route required | ⚠️ Embed only, limited control | ⚠️ DevLink custom form component; still needs external endpoint |
| Video archive | ✅ API route → Mux/Vimeo signed URLs | ⚠️ Separate backend for signed URLs | ⚠️ Embed only, no access control | ⚠️ Embed only; signed URLs need external backend |
| AI background workflows | ✅ Trigger.dev + Vercel AI SDK | ⚠️ Possible but two services to manage | ❌ Not possible | ❌ No server-side runtime; external service required |
| Future client portal | ✅ Natural extension of codebase | ✅ Extensible if backend is well-structured | ❌ Requires full rebuild | ⚠️ DevLink helps with UI; auth/data layer still external |

### Project Considerations

| Criterion | Next.js + Vercel | React + Vite | Framer | Webflow |
|-----------|-----------------|--------------|--------|---------|
| Stacy handoff | ⚠️ New platform for her to learn | ⚠️ New platform for her to learn | ✅ She already knows it | ❌ Different platform, no existing knowledge |
| Nikki can edit content | ✅ Sanity/Contentful visual editor | ⚠️ Needs separate CMS setup | ✅ Visual editor built in | ✅ Visual editor built in |
| Long-term maintainability | ✅ No platform lock-in, open stack | ⚠️ No lock-in, but two services to maintain | ⚠️ Locked to Framer hosting | ⚠️ Locked to Webflow hosting |
| Student team ramp-up | ⚠️ Higher — more pieces to wire together | ⚠️ Familiar stack but split deployment | ✅ Low — visual + React code components | ✅ Low — fully visual |
| Phase 1 discovery fit | ✅ Platform decision deferred, per SOW | ⚠️ New to project, needs evaluation | ✅ Already in use, known quantity | ⚠️ New to project, needs evaluation |

**Key:** ✅ Strong fit · ⚠️ Partial / workaround needed · ❌ Not supported

---

## Recommended Stack (Next.js path)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Framework | Next.js (App Router) | Core web + API layer |
| CMS | Sanity or Contentful | Visual editor for Nikki post-handoff |
| CRM | HubSpot | Lead capture + contact management |
| Video hosting | Mux or Vimeo | Access-controlled archive |
| Background workflows | Trigger.dev + Vercel AI SDK | Event-driven AI agents |
| Deployment | Vercel Pro | Single account owned by Sentinel |

### Suggested agentic workflow architecture

```
Form submission / CRM webhook / site event
        ↓
Next.js API route (receives event)
        ↓
Trigger.dev (queues and orchestrates workflow)
        ↓
AI agent steps (Vercel AI SDK + Claude)
        ↓
Output: HubSpot update / email sent / LinkedIn draft / video tagged
```

## Automation Layer: Make, Zapier, or Trigger.dev

The Sentinel SOW requires an integration layer for three workflows: blog post → LinkedIn, lead capture → CRM, and case study request → approval. The right tool depends on one question: **who maintains these workflows after handoff?**

| Tool | When it fits |
|------|-------------|
| **Trigger.dev** | A developer owns the workflows; logic lives in the Next.js repo alongside the API routes |
| **Make** | Non-technical staff need to own or modify workflows; complex branching is required |
| **Zapier** | Non-technical staff; simpler linear workflows with no branching |

For the approval workflow specifically (case study request → human review → conditional email), Zapier hits its ceiling — that conditional branching is where it struggles. Make handles it; Trigger.dev handles it best if there's a developer involved. See [zapier-vs-make.md](zapier-vs-make.md) for a fuller comparison of the two no-code options.

The Flask + Make demo in this repo illustrates the same three workflows using Make as the integration layer. The patterns transfer (DB-first, fire-and-forget, treat external services as unreliable) even if the specific tool doesn't. If the Sentinel project goes with Trigger.dev, the logic moves from Make scenarios into `app/api/` route handlers and Trigger.dev job definitions — same boundary, different implementation.

**Confirm at kickoff:** who maintains the automation after handoff, and how technical are they? That answer determines the tool.

---

## A Note on Webflow + DevLink

Webflow's **DevLink** is a meaningful capability that the simple comparison table understates. It provides a bidirectional React bridge: React components built outside Webflow can be imported via the Webflow CLI and used on the canvas like native components, and visual components designed in Webflow can be exported as production-ready React/TypeScript. This meaningfully closes the UI complexity gap.

What DevLink does **not** provide is a server-side runtime. Webflow has no API routes, no middleware layer, and no background job runner. So features that require server logic — signed video URLs, session-based auth, CRM API calls, AI workflows — still need an external backend service regardless of DevLink. The distinction is:

- **UI and component complexity** → DevLink closes the gap considerably vs. Framer
- **Server-side logic** → still requires an external backend, same as a plain Vite setup

For Sentinel, this means Webflow + DevLink + an Express or FastAPI backend is a viable architecture — but at that point you're managing the same split-deployment complexity as React + Vite, with Webflow's visual editor as the upside and its hosting lock-in as the downside.

---

## Why Not React + Vite for Sentinel?

React + Vite is the right call for a project like the Hospital Quality Explorer — a data-heavy app with a Python backend, SQLite on disk, and a teaching context that benefits from an explicit client/server separation. For Sentinel it creates more problems than it solves:

- **Split deployment.** Vite produces a static frontend; all the SOW's backend features (auth, CRM, video signing, AI workflows) need a separate server. That means two deployments, two sets of environment variables, and two things that can break — handed off to Nikki and Stacy.
- **No built-in API layer.** Next.js API routes and middleware handle gated routes and CRM calls in the same repo. With Vite you're standing up Express or FastAPI separately, which is extra infrastructure with no benefit for this project.
- **Content editing.** Vite has no CMS story out of the box. You'd wire one up the same way you would with Next.js, but without the deployment simplification Next.js provides.

The one argument for it: if the student team already knows the Vite + Express pattern from another course, the ramp-up is lower. But the operational complexity handed to the client at the end tips the balance back toward Next.js.

---

## The Core Tension

Next.js wins on almost every SOW feature, but **Framer has a real argument in Phase 1**:

- Stacy already knows it
- The existing site lives there
- The SOW gives both parties joint sign-off on platform

If the **feature list** wins the argument (gated content, CRM, AI workflows, future portal) → **Next.js**.

If **handoff risk and student ramp-up** within a 10-week engagement feel too high → **Framer gets you live faster**, even if it hits a ceiling later.

> **Recommendation:** Raise the platform decision explicitly in the Phase 1 discovery meeting. The SOW supports deferring it — use that window to assess Stacy's bandwidth for learning a new stack before committing.

---

## Vercel Pricing and Teaching Context

Vercel's free Hobby tier is available but restricted to personal, non-commercial use. The Sentinel Security site is a commercial project and requires a Pro account at $20/month. The recommended approach for the Roux Institute engagement is one Pro account owned by Sentinel — the student team develops locally and uses preview deployments for review, avoiding per-student costs entirely.

Vercel does not have a formal education discount program for the platform itself. There is no official student pricing for the core hosting product. The one education-adjacent offering is **v0** (Vercel's AI code generator), which offers one free year of premium access to students at a limited set of qualifying institutions — Northeastern is not currently on the list, but a waitlist exists.

For development and teaching purposes, the Hobby tier (free) works well for individual student projects where the non-commercial restriction isn't an issue.

---

## When to Add a Python Backend

For the Sentinel SOW as scoped, a Python backend is not needed. The agentic workflows, CRM integration, and video access control all run cleanly in Next.js API routes using TypeScript.

Python becomes the right call when the work shifts from **orchestrating AI** to **building AI**:

| Trigger | Python adds value because... |
|---------|------------------------------|
| RAG pipelines with real complexity | LangChain, LlamaIndex, Haystack are Python-first; TS ports lag behind |
| Custom ML models | PyTorch, scikit-learn, HuggingFace are Python-only |
| Data processing at scale | Pandas, Polars, DuckDB far ahead of JS equivalents |
| Document/PDF extraction | PyMuPDF, pytesseract significantly more mature than JS alternatives |

For Sentinel, a concrete future trigger would be: "ask a question about our past security incidents" using case study data as a knowledge base. That's a Python RAG service. The architecture at that point becomes:

```
Next.js (web + thin API routes)
        ↓  HTTP
FastAPI service (Python — RAG, embeddings, vector search)
        ↓
Vector DB (Pinecone, Qdrant)
```

FastAPI is the recommended choice for this service — lightweight, async, deploys easily to Railway or Fly.io alongside the Vercel frontend.

---

## Agentic Background Workflows in Detail

For event-driven AI workflows (form submissions, CRM updates, content publishing), the recommended orchestration layer is **Trigger.dev** or **Inngest** sitting between Next.js and the LLM APIs. Both are purpose-built for long-running background jobs in Next.js and handle retries, failure states, and step-level logging.

Concrete examples for the Sentinel project:

- Lead submits gated case study form → AI qualifies and enriches contact in HubSpot, sends personalized follow-up
- Blog post published → AI drafts and queues a LinkedIn post for review
- New video uploaded → AI generates transcript, summary, and tags for archive

**Important:** Vercel's free Hobby tier caps serverless function execution time in ways that break multi-step AI agents. The Pro plan supports function durations up to 800 seconds with Fluid Compute. This is another reason the Sentinel site requires a Pro account.

**Cost profile for agentic tools:**

| Tool | Cost |
|------|------|
| Trigger.dev | Free tier; open source, self-hostable |
| Inngest | Free tier for development; usage-based in production |
| Vercel AI SDK | Free (library) |
| Anthropic / OpenAI | Pay per token; low cost at Sentinel's scale |

Agentic workflows are not in the current SOW scope. Any such features should be raised as a scope addition during Phase 1 discovery and documented with timeline and pricing impact before work begins, per the SOW's scope management clause.

---

## Next.js Learning Curve for Vite + React Developers

For developers already comfortable with Vite and React, the transition to Next.js is relatively shallow. Core React knowledge transfers completely — components, hooks, state, and props are unchanged.

The three meaningful differences to internalize:

**File-based routing.** Next.js uses the file system as the router. A file at `app/blog/page.tsx` automatically becomes the `/blog` route. React Router's explicit configuration is replaced by folder structure. Takes a day or two to internalize but clicks quickly.

**Server Components.** In the App Router, components render on the server by default. Client-side behavior requires opting in with `"use client"` at the top of a file. This is the most common source of confusion coming from Vite — hooks like `useState` will throw errors in server components until the pattern becomes habit.

**API routes.** In Vite you'd reach for a separate Express server. In Next.js a `route.ts` file in the `app` folder creates an endpoint in the same repo. For Sentinel this is where HubSpot calls, video signing, and auth middleware live.

Realistic ramp-up: a week of active building. The official Next.js tutorial (nextjs.org/learn) covers all three areas in 3–4 hours and is genuinely well made.

---

## Next.js vs. Vite for the Hospital Quality Explorer

The Hospital Quality Explorer (HQE) is a useful counterpoint to Sentinel — a project where Vite is clearly the better choice and Next.js would create friction at almost every layer.

| Factor | HQE (Vite is right) | Sentinel (Next.js is right) |
|--------|--------------------|-----------------------------|
| Backend language | Python required (Flask/FastAPI/SQLite/ETL) | No Python needed |
| Database | SQLite on disk — incompatible with serverless | Cloud APIs over HTTP |
| Maps + visualization | Leaflet/Observable Plot need `ssr: false` workarounds in Next.js | No DOM-heavy libraries |
| Auth model | Session-based on persistent server | Middleware on serverless fine |
| SEO requirement | Internal tool, no public indexing needed | Public marketing site |
| Teaching goal | Explicit client/server separation | Unified codebase for handoff |
| Deployment target | EC2 (persistent server) | Vercel (serverless) |

If agentic AI and a Python backend are added to HQE, the architecture becomes Next.js (or Vite) for the frontend with a dedicated FastAPI service handling Python workloads. In that scenario Next.js adds server-side rendering and file-based routing — useful if HQE were to gain public-facing, SEO-indexable hospital profile pages, but unnecessary for a data explorer behind a login. Vite + FastAPI remains the cleaner split for HQE as currently scoped.

---

## Pricing Reference (as of April 2026)

| Platform | Cost |
|----------|------|
| Next.js | Free (open source) |
| Vercel Pro | $20/month (one account, owned by Sentinel) |
| React + Vite | Free (open source); backend hosting ~$7/month on Render or Railway |
| Sanity / Contentful | Free tier available; paid from ~$99/month at scale |
| Framer | $30–$50/month |
| Webflow | $23–$39/month |

> Vercel's Hobby plan is free but restricted to non-commercial personal use. The Sentinel site requires a Pro account.

---

*Generated April 2026 · Roux Institute × Sentinel Security SOW No. 26345*
