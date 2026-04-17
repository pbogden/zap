"""
make_webhook.py
---------------
Utility for firing Make.com webhooks from anywhere in the app.

Usage:
    from .make_webhook import fire_webhook

    fired = fire_webhook("BLOG_POST", {
        "title": "My Post",
        "author": "jane",
        "url": "https://example.com/blog/1",
    })

The event_type maps to a config key: MAKE_WEBHOOK_{EVENT_TYPE}.
If no URL is configured for that event, the call is silently skipped
and False is returned — the app never crashes because of a missing webhook.
"""

import requests
from flask import current_app


def fire_webhook(event_type: str, payload: dict) -> bool:
    """
    POST payload as JSON to the Make webhook URL for event_type.

    Args:
        event_type: One of BLOG_POST | LEAD_CAPTURE | CASE_STUDY_REQUEST
        payload:    Dict of data to send. Must be JSON-serializable.

    Returns:
        True if Make acknowledged the request (2xx), False otherwise.
    """
    config_key = f"MAKE_WEBHOOK_{event_type.upper()}"
    url = current_app.config.get(config_key)

    if not url:
        current_app.logger.debug(
            f"Webhook skipped: no URL configured for {config_key}"
        )
        return False

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        current_app.logger.info(
            f"Webhook fired: {event_type} → {response.status_code}"
        )
        return True

    except requests.exceptions.Timeout:
        current_app.logger.error(f"Webhook timeout: {event_type}")
        return False

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Webhook error ({event_type}): {e}")
        return False
