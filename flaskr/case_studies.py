"""
case_studies.py  —  Stage 3
-----------------------------
Gated case study showcase. Visitors can browse case study summaries and
request access to the full PDF.

When a request is submitted, we:
  1. Save the request to the database with status='pending'
  2. Fire a webhook to Make, which runs an approval workflow:
       - Emails the reviewer with the request details and two buttons:
         [Approve] / [Decline]
       - If approved: Make sends the requester an email with the download link
       - If declined: Make sends a polite decline email

This demonstrates Make's ability to handle asynchronous, human-in-the-loop
workflows — something Flask alone can't do without significant extra code.
"""

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from .db import get_db
from .make_webhook import fire_webhook

bp = Blueprint("case_studies", __name__, url_prefix="/case-studies")


@bp.route("/")
def index():
    db = get_db()
    studies = db.execute(
        "SELECT id, title, summary, industry FROM case_study ORDER BY industry, title"
    ).fetchall()
    return render_template("case_studies/index.html", studies=studies)


@bp.route("/<int:id>/request-access", methods=("GET", "POST"))
def request_access(id):
    db = get_db()
    study = db.execute(
        "SELECT id, title, industry FROM case_study WHERE id = ?", (id,)
    ).fetchone()

    if study is None:
        flash("Case study not found.")
        return redirect(url_for("case_studies.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()

        error = None
        if not name:
            error = "Your name is required."
        elif not email:
            error = "Your email address is required."
        elif "@" not in email:
            error = "Please enter a valid email address."

        if error is None:
            # 1. Save the request
            db.execute(
                "INSERT INTO case_study_request"
                " (case_study_id, requester_name, requester_email, requester_company)"
                " VALUES (?, ?, ?, ?)",
                (id, name, email, company),
            )
            db.commit()

            request_id = db.execute(
                "SELECT last_insert_rowid()"
            ).fetchone()[0]

            # 2. Fire webhook — Make handles the approval flow from here
            webhook_fired = fire_webhook("CASE_STUDY_REQUEST", {
                "request_id": request_id,
                "case_study_id": study["id"],
                "case_study_title": study["title"],
                "case_study_industry": study["industry"],
                "requester_name": name,
                "requester_email": email,
                "requester_company": company,
                # Make uses this URL to fetch the file if the request is approved
                "file_url": db.execute(
                    "SELECT file_url FROM case_study WHERE id = ?", (id,)
                ).fetchone()["file_url"],
            })

            db.execute(
                "UPDATE case_study_request SET webhook_fired = ? WHERE id = ?",
                (1 if webhook_fired else 0, request_id),
            )
            db.commit()

            flash(
                f"Your request for '{study['title']}' has been submitted. "
                "We'll review it and get back to you by email."
            )
            return redirect(url_for("case_studies.index"))

        flash(error)

    return render_template("case_studies/request.html", study=study)
