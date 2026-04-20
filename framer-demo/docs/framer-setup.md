# Framer Setup — Building the Contact Form

This guide walks through building and publishing the demo site in Framer's
free plan. No credit card required at any step.

---

## Step 1 — Create a Framer account

1. Go to [framer.com](https://framer.com) and click **Get Started**
2. Sign up with Google or email — no payment method required
3. You'll land in the Framer dashboard

---

## Step 2 — Create a new project

1. Click **New Project**
2. Choose **Blank** (not a template — you want to build this from scratch
   so students can see every decision)
3. Name it `sentinel-contact-demo`

---

## Step 3 — Build the page

You're now in Framer's visual editor. The canvas is blank.

### Add a heading

1. Press `T` to add a text element
2. Type: `Contact Sentinel Security`
3. In the right panel, set font size to 40, weight to Bold

### Add a subtitle

1. Press `T` again for another text element
2. Type: `Interested in working with us? Fill out the form below.`
3. Set font size to 18, color to a medium grey

### Add the form

1. In the left panel, click **Insert** (or press `I`)
2. Search for **Form** and drag it onto the canvas
3. The default form includes Name and Email fields — you'll add more

### Configure form fields

Click the form to select it. In the right panel you'll see the form's fields.
Add or rename fields so you have exactly these four, in this order:

| Field label | Field name (important!) | Type | Required |
|---|---|---|---|
| Name | `name` | Text | Yes |
| Email | `email` | Email | Yes |
| Company | `company` | Text | No |
| Message | `message` | Textarea | Yes |

> **Why field names matter:** When Framer sends the webhook payload, it uses
> the field *name* (not the label) as the JSON key. Make will look for
> `name`, `email`, `company`, and `message` exactly. If you name a field
> `full-name` instead of `name`, the Make scenario will receive
> `full-name` and the HubSpot mapping will break.
>
> This is the Framer equivalent of the `name` attribute on an HTML input —
> a useful thing to point out to students who've built forms in code.

### Configure the submit button

Click the submit button. In the right panel, change the label to
`Send Message`.

---

## Step 4 — Connect the form to Make

You'll need your Make webhook URL before completing this step. If you
haven't built the Make scenario yet, go to [make-scenario.md](make-scenario.md)
and complete Steps 1–2 (creating the webhook trigger) before continuing here.

Once you have the Make webhook URL:

1. Select the form on the canvas
2. In the right panel, find **Send To**
3. Click **Add…** next to Send To
4. Select **Webhook**
5. Paste your Make webhook URL (starts with `https://hook.us1.make.com/...`)
6. Click **Save**

> **What Framer sends:** On submission, Framer POSTs this JSON to Make:
> ```json
> {
>   "name": "Jordan Kim",
>   "email": "jordan@example.com",
>   "company": "Cascade Industrial",
>   "message": "We're evaluating security vendors..."
> }
> ```
> This is the same payload shape as the Flask demo's `fire_webhook()` call
> in `leads.py`. Make can't tell the difference.

---

## Step 5 — Style the page (optional but recommended)

Even a minimal treatment makes the demo feel more real. A few quick wins:

- Set the page background to `#1a1a2e` (the same dark navy used in the
  Flask demo's CSS)
- Set form field backgrounds to white, text to dark
- Set the submit button background to `#1a1a2e`, text to white
- Center everything on the canvas with a max-width of 600px

This takes about 5 minutes and makes the comparison to the Flask site
more visually coherent.

---

## Step 6 — Publish the site

1. Click the **Publish** button in the top-right corner
2. Framer will assign your site a URL like:
   `sentinel-contact-demo.framer.website`
3. Click **Publish to framer.website**

Your site is now live and the form is active. The "Made in Framer" badge
will appear in the bottom-left corner — this is expected on the free plan
and doesn't affect functionality.

> **Free plan publishing note:** Framer publishes to a `.framer.website`
> subdomain on the free plan. For a classroom demo this is perfectly fine.
> A custom domain requires the Basic plan ($10/month).

---

## Step 7 — Test the form

1. Open your published site URL
2. Fill in all four fields with test data
3. Click **Send Message**
4. Check Make's scenario history — you should see a successful run
5. Check Slack's `#leads` channel and HubSpot's contacts

If the form submits but Make doesn't fire, double-check that:
- The webhook URL in Framer's Send To setting is correct
- The Make scenario is toggled **ON**
- Make's scenario has been run once to teach it the payload structure

---

## Free Plan Limits to Know

| Limit | Value | Impact on demo |
|---|---|---|
| Form submissions | 1,000/month | Fine for classroom use |
| Bandwidth | 100MB/month | Fine for a demo site |
| Custom domain | Not available | Use `.framer.website` subdomain |
| Framer badge | Always visible | Cosmetic only |

> Earlier research suggested the free plan had a 50-submission lifetime cap,
> but Framer updated their plans in late 2025. The current free plan allows
> 1,000 submissions per month, which is more than sufficient for classroom use.
> Always verify current limits at [framer.com/pricing](https://framer.com/pricing)
> before class.
