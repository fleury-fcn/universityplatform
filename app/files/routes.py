import os

from flask import abort, send_file
from flask_login import current_user, login_required

from app.core.files import INLINE, can_download, path_of
from app.extensions import db
from app.models.files import StoredFile

from . import bp


@bp.route("/<int:file_id>/<path:name>")
@login_required
def download(file_id, name):
    stored = db.get_or_404(StoredFile, file_id)
    if not can_download(current_user, stored):
        abort(404)
    path = path_of(stored)
    if not os.path.exists(path):
        abort(404)
    response = send_file(
        path,
        mimetype=stored.mime_type,
        as_attachment=stored.extension not in INLINE,
        download_name=stored.original_name,
        conditional=True,
    )
    # Privé (jamais dans un cache partagé) mais conservé sur l'appareil pour la consultation hors ligne.
    response.headers["Cache-Control"] = "private, max-age=604800"
    return response
