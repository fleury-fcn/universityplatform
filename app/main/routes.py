from flask import abort, current_app, jsonify, make_response, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_required
from sqlalchemy import text

from app.core.security import is_safe_redirect
from app.extensions import db

from . import bp


@bp.route("/")
@login_required
def home():
    return render_template("main/home.html")


@bp.route("/langue/<code>")
def set_language(code):
    if code not in current_app.config["LANGUAGES"]:
        abort(404)
    target = request.args.get("next")
    response = make_response(redirect(target if is_safe_redirect(target) else url_for("main.home")))
    response.set_cookie("lang", code, max_age=365 * 24 * 3600, samesite="Lax", httponly=True)
    return response


@bp.route("/hors-ligne")
def offline():
    return render_template("main/offline.html")


@bp.route("/sante")
def health():
    db.session.execute(text("SELECT 1"))
    return jsonify(status="ok")


@bp.route("/sw.js")
def service_worker():
    # Servi à la racine pour que le service worker contrôle tout le site.
    version = current_app.config["ASSET_VERSION"]
    shell_urls = [url_for("main.offline")] + [
        url_for("static", filename=f, v=version)
        for f in ("css/app.css", "js/app.js", "img/icons.svg", "img/logo.png", "img/icon-192.png")
    ]
    response = make_response(render_template("sw.js", shell_urls=shell_urls))
    response.mimetype = "text/javascript"
    response.headers["Cache-Control"] = "no-cache"
    return response


@bp.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(
        current_app.static_folder, "manifest.webmanifest", mimetype="application/manifest+json"
    )
