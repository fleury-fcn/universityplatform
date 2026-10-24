"""En-têtes de sécurité HTTP, contrôle d'accès par rôle et redirections sûres."""
import secrets
from functools import wraps
from urllib.parse import urljoin, urlsplit

from flask import abort, g, make_response, request
from flask_login import current_user, login_required

ROLE_STUDENT = "etudiant"
ROLE_TEACHER = "enseignant"
ROLE_ADMIN = "admin"
ROLES = (ROLE_STUDENT, ROLE_TEACHER, ROLE_ADMIN)


def role_required(*roles):
    """Restreint une vue aux rôles donnés (l'administrateur a toujours accès)."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != ROLE_ADMIN and current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


admin_required = role_required(ROLE_ADMIN)
staff_required = role_required(ROLE_TEACHER, ROLE_ADMIN)


def no_store(view):
    """Empêche la mise en cache (navigateur et hors ligne) d'une page sensible."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store"
        return response

    return wrapped


def is_safe_redirect(target):
    """Accepte uniquement une redirection vers ce même site."""
    if not target:
        return False
    host = urlsplit(request.host_url)
    dest = urlsplit(urljoin(request.host_url, target))
    return dest.scheme in ("http", "https") and dest.netloc == host.netloc


def csp_nonce():
    if "csp_nonce" not in g:
        g.csp_nonce = secrets.token_urlsafe(16)
    return g.csp_nonce


def init_app(app):
    app.jinja_env.globals["csp_nonce"] = csp_nonce

    @app.after_request
    def set_security_headers(response):
        nonce = g.get("csp_nonce", "")
        script_src = f"'self' 'nonce-{nonce}'" if nonce else "'self'"
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            f"script-src {script_src}; "
            "style-src 'self'; "
            "img-src 'self' data: https://tile.openstreetmap.org; "
            "connect-src 'self'; font-src 'self'; object-src 'none'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'; "
            "manifest-src 'self'; worker-src 'self'",
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(self)")
        if request.is_secure:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return response
