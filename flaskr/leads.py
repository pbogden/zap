"""
leads.py  —  Stage 2
---------------------
Lead capture form — Stage 2.

When a visitor submits the contact form, we:
  1. Save the lead to the database (so we have a record regardless of Make)
  2. Fire a webhook to Make, which:
       - Creates a contact in HubSpot (or equivalent CRM)
       - Sends a confirmation email to the prospect
       - Notifies the team on Slack

The separation is intentional: the DB write and the webhook are independent.
If Make is down, the lead is still saved. This is a good pattern to discuss
with students — "what happens when your integration fails?"
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from .db import get_db
from .make_webhook import fire_webhook

bp = Blueprint("leads", __name__, url_prefix="/contact")


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        message = request.form.get("message", "").strip()

        error = None
        if not name:
            error = "Your name is required."
        elif not email:
            error = "Your email address is required."
        elif "@" not in email:
            error = "Please enter a valid email address."
        elif not message:
            error = "A message is required."

        if error is None:
            db = get_db()

            # 1. Save to database first — this always happens
            db.execute(
                "INSERT INTO lead (name, email, company, message)"
                " VALUES (?, ?, ?, ?)",
                (name, email, company, message),
            )
            db.commit()

            lead_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

            # 2. Fire webhook to Make — this may silently fail if not configured
            webhook_fired = fire_webhook("LEAD_CAPTURE", {
                "name": name,
                "email": email,
                "company": company,
                "message": message,
            })

            # 3. Update the record so we know whether Make was notified
            db.execute(
                "UPDATE lead SET webhook_fired = ? WHERE id = ?",
                (1 if webhook_fired else 0, lead_id),
            )
            db.commit()

            flash("Thanks for reaching out — we'll be in touch shortly.")
            return redirect(url_for("leads.index"))

        flash(error)

    return render_template("leads/index.html")
