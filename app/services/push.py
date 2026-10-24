"""Notifications push web (facultatives).

Actives seulement si VAPID_PUBLIC_KEY et VAPID_PRIVATE_KEY sont définies. Les envois
sont préparés pendant la requête puis partent en arrière-plan une fois la réponse
validée, pour ne jamais ralentir l'utilisateur.
"""
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from flask import current_app, g

from app.extensions import db

log = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="push")


def push_enabled(app=None):
    config = (app or current_app).config
    return bool(config.get("VAPID_PUBLIC_KEY") and config.get("VAPID_PRIVATE_KEY"))


def queue_push(user_ids, title, url):
    """Mémorise un envoi ; il partira après une réponse réussie (voir init_app)."""
    if push_enabled():
        g.setdefault("pending_push", []).append((list(user_ids), title, url))


def _send_all(app, jobs):
    from pywebpush import WebPushException, webpush

    expired = []
    for subscription, payload in jobs:
        try:
            webpush(
                subscription_info=subscription,
                data=payload,
                vapid_private_key=app.config["VAPID_PRIVATE_KEY"],
                vapid_claims={"sub": app.config["VAPID_CONTACT"]},
                ttl=24 * 3600,
                timeout=10,
            )
        except WebPushException as err:
            status = getattr(err.response, "status_code", None)
            if status in (404, 410):
                expired.append(subscription["endpoint"])
            else:
                log.warning("Échec d'envoi push : %s", err)
        except Exception:  # réseau indisponible, etc. : ne doit jamais faire planter l'appli
            log.exception("Erreur inattendue lors d'un envoi push")
    if expired:
        from app.models import PushSubscription

        with app.app_context():
            PushSubscription.query.filter(PushSubscription.endpoint.in_(expired)).delete()
            db.session.commit()


def init_app(app):
    @app.after_request
    def dispatch_pending_push(response):
        pending = g.pop("pending_push", None)
        if not pending or response.status_code >= 400:
            return response
        from app.models import PushSubscription

        jobs = []
        for user_ids, title, url in pending:
            payload = json.dumps({"title": title, "url": url})
            for sub in PushSubscription.query.filter(PushSubscription.user_id.in_(user_ids)):
                jobs.append(({"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}}, payload))
        if jobs:
            _executor.submit(_send_all, app, jobs)
        return response
