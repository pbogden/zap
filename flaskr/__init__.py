import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        # Make webhook URLs — loaded from .env via python-dotenv
        MAKE_WEBHOOK_BLOG_POST=os.environ.get("MAKE_WEBHOOK_BLOG_POST"),
        MAKE_WEBHOOK_LEAD_CAPTURE=os.environ.get("MAKE_WEBHOOK_LEAD_CAPTURE"),
        MAKE_WEBHOOK_CASE_STUDY_REQUEST=os.environ.get("MAKE_WEBHOOK_CASE_STUDY_REQUEST"),
        SENTINEL_REVIEW_EMAIL=os.environ.get("SENTINEL_REVIEW_EMAIL"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")

    # Stage 2: Lead capture
    from . import leads
    app.register_blueprint(leads.bp)

    # Stage 3: Gated case studies
    from . import case_studies
    app.register_blueprint(case_studies.bp)

    return app
