# Stage 1 — Blog: Reaching an Audience

## Functional requirement

The client wants blog content to reach subscribers automatically, without manually distributing each post.

## Why RSS/Atom — not a webhook

The question before writing any code: does this require push or pull?

**Push** (webhook) fires the moment a post is published and notifies a specific service immediately. Think of it like a text message — the moment something happens, you tell someone about it. This makes sense when two different people are involved: one person writes and publishes the post, and a different person — say, a social media manager — needs to know right away so they can share it before the news cycle moves on.

**Pull** (RSS/Atom feed) works the other way: instead of your app notifying anyone, interested parties check in on their own schedule and pick up whatever is new. Think of it like a newspaper on the doorstep — it's there when you want it, and you don't need to call the publisher every morning to ask if there's a new edition. Newsletter platforms (Mailchimp, Buttondown, Substack) do exactly this: you give them your feed URL once, and they check it automatically and email your subscribers whenever something new appears.

For a small team where the same person writes the post and shares it on LinkedIn, there's no one to notify who doesn't already know. RSS is the right answer: set it up once, point a newsletter tool at it, and new posts reach subscribers automatically.

Add notifications later if the team grows and blog publishing becomes someone's job while sharing it on social becomes someone else's.

---

## What Flask adds

A single `/feed` route in `blog.py` that returns an RSS 2.0 (or Atom) document. The route queries the database for recent posts and serializes them as feed items.

```python
@bp.route('/feed')
def feed():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC LIMIT 20'
    ).fetchall()
    # return RSS/Atom XML
```

Key fields in each feed item:
- `<title>` — post title
- `<link>` — full URL to the post
- `<description>` — post body or summary
- `<pubDate>` — publication timestamp
- `<guid>` — unique identifier (typically the post URL); feed readers use this to avoid re-processing old items

---

## Testing the feed

With the app running:

```bash
curl http://localhost:5000/feed
```

You should see well-formed XML. Validate it at [validator.w3.org/feed](https://validator.w3.org/feed/) before pointing a real newsletter tool at it.

To connect a newsletter platform: paste `http://your-domain.com/feed` into the RSS import field of Mailchimp, Buttondown, or similar. The platform polls on its own schedule and sends new items to subscribers automatically.

---

## Discussion: when would you add push?

RSS covers the case where the client wants to distribute content to subscribers. A webhook becomes useful when:

- The person publishing and the person sharing are different people, and timing matters
- The client wants immediate notifications (Slack, Teams, email) on publish
- The downstream service can't or won't poll (some CRMs, internal tools)

When that coordination problem exists, Stage 2's pattern — write to DB first, then call external services — applies equally to a blog publish notification.

---

## Discussion: what about drafts?

The current Flaskr blog publishes immediately on save. In a production app you'd add a `published` boolean to the `post` table and gate the feed on it — only published posts appear in the feed, and only published posts trigger any downstream notification.

This is a natural extension exercise: add the column, update the feed query, and update the blog create/edit form to include a publish toggle.
