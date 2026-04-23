"""
blog.py
-------
Standard Flaskr blog blueprint with two additions for Stage 1:

  1. fire_webhook() notifies Make when a post is published (push model).
     Make cross-posts to LinkedIn and sends a Slack notification.

  2. /feed serves an RSS 2.0 feed of recent posts (pull model).
     Make (or any RSS reader / newsletter tool) can poll this instead
     of waiting for a webhook.

Search for "# STAGE 1" to find the relevant additions.
"""

from email.utils import format_datetime
from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, url_for, Response
)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db
from .make_webhook import fire_webhook  # STAGE 1: import the webhook utility

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()

            # Fetch the new post's id so we can build its URL
            post_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            # STAGE 1: Fire a webhook to Make after the post is saved.
            # Make will pick this up and:
            #   - Post to LinkedIn
            #   - Send a Slack notification to #content channel
            fire_webhook("BLOG_POST", {
                "title": title,
                "author": g.user["username"],
                "url": url_for("blog.detail", id=post_id, _external=True),
                "summary": body[:200],  # First 200 chars as a preview
            })

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (id,),
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id>/detail")
def detail(id):
    post = get_post(id, check_author=False)
    return render_template("blog/detail.html", post=post)


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?",
                (title, body, id),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))


# STAGE 1 (alternate): RSS 2.0 feed
# ----------------------------------
# Exposes the 20 most recent posts as a standard RSS feed at /feed.
#
# This is the *pull* counterpart to the webhook's *push* model:
#   - Webhook: Flask notifies Make the moment a post is published
#   - RSS:     Make (or any tool) polls /feed on a schedule and acts
#              on new items it hasn't seen before
#
# Both approaches end up at the same Make modules (Slack, LinkedIn).
# The difference is who initiates the exchange and when.
#
# RSS 2.0 is used here (over Atom) for maximum tool compatibility —
# Make, Mailchimp, Zapier, and most RSS readers all speak RSS 2.0
# without any extra configuration.

@bp.route("/feed")
def feed():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
        " LIMIT 20"
    ).fetchall()

    base_url = request.url_root.rstrip("/")
    feed_url = url_for("blog.feed", _external=True)
    site_url = url_for("blog.index", _external=True)

    # Build pub dates — SQLite returns strings; format_datetime needs a datetime
    from datetime import datetime, timezone

    def pub_date(row):
        # SQLite CURRENT_TIMESTAMP format: "YYYY-MM-DD HH:MM:SS"
        dt = datetime.strptime(str(row["created"]), "%Y-%m-%d %H:%M:%S")
        return format_datetime(dt.replace(tzinfo=timezone.utc))

    items = []
    for post in posts:
        post_url = url_for("blog.detail", id=post["id"], _external=True)
        # Escape any XML-significant characters in title and body
        title = post["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        description = post["body"][:500].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        items.append(
            f"""    <item>
      <title>{title}</title>
      <link>{post_url}</link>
      <guid isPermaLink="true">{post_url}</guid>
      <pubDate>{pub_date(post)}</pubDate>
      <author>{post["username"]}</author>
      <description>{description}</description>
    </item>"""
        )

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Blog</title>
    <link>{site_url}</link>
    <description>Recent posts</description>
    <language>en-us</language>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"
               xmlns:atom="http://www.w3.org/2005/Atom"/>
{chr(10).join(items)}
  </channel>
</rss>"""

    return Response(rss, mimetype="application/rss+xml")
