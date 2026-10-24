from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from app.core.security import is_safe_redirect, no_store
from app.extensions import db
from app.models import Notification, utcnow
from app.services.notifications import mark_read

from . import bp


@bp.app_context_processor
def inject_unread_count():
    if not current_user.is_authenticated:
        return {}
    count = Notification.query.filter_by(user_id=current_user.id, read_at=None).count()
    return {"unread_notifications": count}


@bp.route("/")
@login_required
@no_store
def index():
    page = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .paginate(per_page=30, error_out=False)
    )
    return render_template("notifications/index.html", page=page)


@bp.route("/<int:notification_id>")
@login_required
def open_notification(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    if notification.read_at is None:
        notification.read_at = utcnow()
        db.session.commit()
    target = notification.url
    return redirect(target if is_safe_redirect(target) else url_for("notifications.index"))


@bp.route("/tout-lire", methods=["POST"])
@login_required
def read_all():
    mark_read(current_user.id)
    db.session.commit()
    return redirect(url_for("notifications.index"))
