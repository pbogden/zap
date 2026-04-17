# Stage 1 — Blog Post → Make → Slack + LinkedIn

## What This Demonstrates

When a logged-in user publishes a blog post, Flask fires a POST request to a
Make webhook URL. Make receives the payload and fans it out to two destinations:
a Slack channel and a LinkedIn post.

Your Flask app has no LinkedIn SDK, no Slack SDK, and no API keys for either.
It just fires and forgets.

---

## The Payload Flask Sends

```json
{
  "title": "Zero Trust in the Enterprise: What Actually Works",
  "author": "nikki",
  "url": "http://localhost:5000/1/detail",
  "summary": "After three years of zero-trust implementations across financial..."
}
```

---

## Building the Make Scenario

### Step 1 — Create a new scenario

1. Log into [make.com](https://make.com) and open your workspace
2. Click **Create a new scenario**
3. Search for and select **Webhooks** as your first module

### Step 2 — Configure the Custom Webhook trigger

1. Add a **Custom Webhook** module
2. Click **Add** to create a new webhook
3. Name it `sentinel-blog-post`
4. Click **Save** — Make will generate a URL like:
   `https://hook.us1.make.com/abc123xyz`
5. Copy this URL — you'll put it in your `.env` as `MAKE_WEBHOOK_BLOG_POST`

**Teach Make the payload structure:**
1. Click **Re-determine data structure**
2. In a separate terminal, run the Flask app and publish a test post
3. Make will receive the payload and map the fields automatically
4. You should see `title`, `author`, `url`, and `summary` appear as available fields

### Step 3 — Add a Slack module

1. Click the **+** after the webhook module
2. Search for **Slack** and select **Create a Message**
3. Connect your Slack workspace (OAuth flow)
4. Configure:
   - **Channel:** `#content` (or whichever channel you want)
   - **Text:**
     ```
     📝 New post published: *{{title}}*
     By {{author}} — {{url}}
     ```

### Step 4 — Add a LinkedIn module

1. Click **+** after the Slack module
2. Search for **LinkedIn** and select **Create a Share**
3. Connect your LinkedIn account
4. Configure:
   - **Visibility:** Public
   - **Commentary:**
     ```
     New from Sentinel Security: {{title}}

     {{summary}}

     Read more → {{url}}
     ```

### Step 5 — Activate and test

1. Toggle the scenario **ON** (bottom left)
2. Make sure your `.env` has the webhook URL set:
   ```
   MAKE_WEBHOOK_BLOG_POST=https://hook.us1.make.com/abc123xyz
   ```
3. Restart Flask and publish a post
4. Check Make's **History** tab — you should see a successful run
5. Check Slack and LinkedIn

---

## Error Handling to Discuss

The `fire_webhook()` utility in `make_webhook.py` has a 5-second timeout and
catches all exceptions. Flask will never crash or return an error to the user
because of a Make failure. Ask students:

- What happens to the post if Make is down?
- Is that the right behavior? When might it not be?
- How would you build a retry mechanism?

---

## Scenario Flow Diagram

```
Flask (blog.py)
  │
  │  POST { title, author, url, summary }
  ▼
Make: Custom Webhook
  │
  ├──► Slack: Create Message
  │      Channel: #content
  │      Text: "📝 New post: {title} ..."
  │
  └──► LinkedIn: Create Share
         Commentary: "{title}\n\n{summary}\n\n{url}"
```

---

## Alternate Approach: RSS Polling

The blog also exposes an RSS 2.0 feed at `/feed`. This is the *pull* counterpart
to the webhook's *push* model — instead of Flask notifying Make the moment a post
is published, Make polls the feed on a schedule and acts on items it hasn't seen
before.

### When to use each

| | Webhook (push) | RSS (pull) |
|---|---|---|
| Delivery timing | Immediate | On Make's polling schedule (min. ~15 min) |
| Flask complexity | One function call | One route |
| Make trigger | Custom Webhook | RSS / Atom Feed |
| Works without Make | No — needs a listener | Yes — any RSS reader works |
| Good for | Real-time notifications | Newsletter tools, feed aggregators |

For a live demo in class, the webhook is more satisfying — you publish a post and
Slack lights up immediately. RSS is better for discussing the broader ecosystem:
Mailchimp, Substack, Buttondown, and most newsletter platforms can drive an
RSS-to-email campaign directly from `/feed` with no Make involved at all.

### Building the RSS scenario in Make

> **Free plan note:** Make polls RSS feeds on a 15-minute minimum interval,
> so you can't demonstrate a live RSS trigger in real time without waiting.
> Instead, use Make's **Run once** button to trigger the scenario manually
> after publishing a post — it simulates an immediate poll and shows the full
> flow without the wait. See [free-tier.md](free-tier.md) for details.

1. Create a new scenario
2. Add an **RSS / Atom Feed** trigger module
3. Set the **Feed URL** to `http://localhost:5000/feed`
   (use your deployed URL in production)
4. Set the polling interval — 15 minutes is the minimum on free plans
5. Add the same Slack and LinkedIn modules from the webhook scenario
6. Map `{{title}}`, `{{link}}`, and `{{description}}` from the feed item
   to the same fields you used before

Make tracks which items it has already processed using the `<guid>` field,
so it won't re-post old content when it polls.

### Updated flow diagram

```
Make: RSS Feed trigger (polls /feed every N minutes)
  │
  │  New item detected: { title, link, description, pubDate }
  ▼
  ├──► Slack: Create Message
  │      Text: "📝 New post: {title} — {link}"
  │
  └──► LinkedIn: Create Share
         Commentary: "{title}\n\n{description}\n\n{link}"
```

### Discussion question

The webhook fires the moment a post is saved, even during a draft or testing
session. The RSS feed only exposes posts that are already public. In a production
app, how would you add a `published` boolean to the `post` table and gate both
the feed and the webhook on it?
