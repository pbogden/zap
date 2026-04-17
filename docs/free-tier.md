# Running the Demo on Make's Free Plan

This demo runs on Make's free plan with no meaningful limitations for an
instructor-led walkthrough. Here's what to know before class.

---

## What the free plan gives you

- 1,000 credits/month — far more than a demo will use
- Access to all 3,000+ app integrations
- Webhook triggers — **respond instantly**, not on a polling schedule
- The visual scenario builder, routers, and filters

## The one constraint: 2 active scenarios at a time

Stage 3 requires 3 scenarios (request handler + approve + decline), which
exceeds the free plan's limit. The workaround for a sequential instructor
demo is to swap scenarios in and out as you move between stages:

| Demo moment | Active scenarios |
|---|---|
| Stage 1 walkthrough | `sentinel-blog-post` |
| Stage 2 walkthrough | `sentinel-lead-capture` (deactivate Stage 1) |
| Stage 3 walkthrough | `sentinel-cs-approve` + `sentinel-cs-decline` (deactivate Stage 2, add Stage 3 handler) |

Toggling a scenario on or off takes about 10 seconds in Make's UI — flip the
switch in the bottom-left corner of any open scenario. In practice this is
barely noticeable during a live demo, and you can frame it honestly:

> *"On the free plan you get two active scenarios at once — so we'll swap as
> we go. In production you'd have all of these running simultaneously, which
> is what the $9/month Core plan unlocks."*

That's a more useful thing to say than pretending the constraint doesn't exist.

---

## Service-by-service free tier status

| Service | Free tier | Notes |
|---|---|---|
| Make.com | ✅ | 1,000 credits/month, 2 active scenarios |
| Slack | ✅ | Webhooks and bot messages work fully |
| HubSpot | ✅ | Free CRM supports contact creation via API |
| Gmail | ✅ | Make's Gmail module works on free |
| LinkedIn | ⚠️ | See below |
| RSS polling | ⚠️ | 15-minute minimum interval on free |

---

## LinkedIn: use Slack instead for the demo

LinkedIn personal posting requires OAuth app setup and approval through
LinkedIn's Developer Portal — possible, but not something you want to debug
in front of a class. For the Stage 1 demo, replace the LinkedIn module with
a second Slack message to a different channel (e.g. `#linkedin-preview`).

The scenario structure, the webhook payload, and every teaching point about
Make are identical. You can note that LinkedIn is the real-world destination
and show the module configuration without a live connection:

> *"In the actual client scenario this module posts to LinkedIn. The config
> is exactly the same — we just can't fire a live LinkedIn post in class
> without going through their partner approval process. The Slack message
> here proves the webhook fired and Make received the payload."*

This is also a reasonable production choice for a demo environment — you
probably don't want test posts appearing on a real LinkedIn page anyway.

---

## RSS polling: walk through the config, skip the wait

Make's free plan polls RSS feeds on a 15-minute minimum interval, so you
can't demonstrate a live RSS trigger in real time. Two options:

1. **Walk through the Make config** — show students the RSS trigger module,
   explain the polling model, and contrast it with the webhook approach.
   The teaching point lands without a live trigger.

2. **Switch to manual run** — in Make, any scenario can be triggered
   manually with the "Run once" button regardless of its schedule. Publish
   a post, then click "Run once" in the RSS scenario to simulate an
   immediate poll. This demonstrates the full flow without waiting.

The "Run once" approach is actually cleaner for a demo — you control exactly
when it fires.

---

## Upgrading to Core ($9/month)

If you want all scenarios active simultaneously or need the RSS polling to
work in real time, Make's Core plan removes both constraints. At $9/month
it's the only paid service the demo requires — everything else runs free.

The free plan is fully sufficient for an instructor-led demo.
