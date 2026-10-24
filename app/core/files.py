"""Dépôt et téléchargement sécurisés de fichiers.

- extension autorisée ET signature binaire cohérente (un .pdf doit être un vrai PDF) ;
- taille limitée par catégorie ;
- nom de stockage aléatoire, hors du dossier public ;
- téléchargement uniquement via une route qui vérifie les droits.
"""
import os
import secrets
import zipfile

from flask import current_app
from flask_babel import gettext as _
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.files import StoredFile

MB = 1024 * 1024

OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # anciens formats Office (.doc, .xls, .ppt)


def _zip_contains(path, prefix):
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            if prefix == "mimetype":
                return "mimetype" in names and zf.read("mimetype").startswith(b"application/vnd.oasis.opendocument")
            return "[Content_Types].xml" in names and any(n.startswith(prefix) for n in names)
    except (zipfile.BadZipFile, OSError, KeyError):
        return False


def _is_text(path):
    with open(path, "rb") as f:
        chunk = f.read(64 * 1024)
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        try:
            chunk.decode("latin-1")
        except UnicodeDecodeError:
            return False
    return True


# extension -> (type MIME, vérification de signature : préfixe binaire ou fonction(chemin))
FILE_TYPES = {
    "pdf": ("application/pdf", b"%PDF-"),
    "png": ("image/png", b"\x89PNG\r\n\x1a\n"),
    "jpg": ("image/jpeg", b"\xff\xd8\xff"),
    "jpeg": ("image/jpeg", b"\xff\xd8\xff"),
    "doc": ("application/msword", OLE),
    "xls": ("application/vnd.ms-excel", OLE),
    "ppt": ("application/vnd.ms-powerpoint", OLE),
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",
             lambda p: _zip_contains(p, "word/")),
    "xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
             lambda p: _zip_contains(p, "xl/")),
    "pptx": ("application/vnd.openxmlformats-officedocument.presentationml.presentation",
             lambda p: _zip_contains(p, "ppt/")),
    "odt": ("application/vnd.oasis.opendocument.text", lambda p: _zip_contains(p, "mimetype")),
    "ods": ("application/vnd.oasis.opendocument.spreadsheet", lambda p: _zip_contains(p, "mimetype")),
    "odp": ("application/vnd.oasis.opendocument.presentation", lambda p: _zip_contains(p, "mimetype")),
    "csv": ("text/csv", _is_text),
    "txt": ("text/plain", _is_text),
}

DOCUMENTS = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "odt", "ods", "odp", "csv", "txt"}
IMAGES = {"png", "jpg", "jpeg"}
INLINE = {"pdf", "png", "jpg", "jpeg"}

# Règles par catégorie : extensions autorisées et taille maximale.
CATEGORIES = {
    "resource": (DOCUMENTS | IMAGES, 20 * MB),
    "message": (DOCUMENTS | IMAGES, 5 * MB),
    "tip": (DOCUMENTS | IMAGES, 10 * MB),
}


class UploadError(ValueError):
    pass


def category_rules(category):
    extensions, max_bytes = CATEGORIES[category]
    return extensions, min(max_bytes, current_app.config["MAX_CONTENT_LENGTH"])


def accept_attribute(category):
    return ",".join(f".{ext}" for ext in sorted(CATEGORIES[category][0]))


def _folder(category):
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], category)
    os.makedirs(path, exist_ok=True)
    return path


def path_of(stored):
    return os.path.join(_folder(stored.category), stored.stored_name)


def save_upload(file_storage, category, owner_id):
    """Valide et enregistre un fichier. Lève UploadError avec un message lisible."""
    extensions, max_bytes = category_rules(category)
    original = (file_storage.filename or "").strip()
    safe_name = secure_filename(original) or "fichier"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in extensions or ext not in FILE_TYPES:
        raise UploadError(_("Type de fichier non autorisé (%(ext)s).", ext=ext or "?"))
    if not safe_name.lower().endswith("." + ext):
        safe_name = f"{safe_name}.{ext}"

    stored_name = f"{secrets.token_hex(16)}.{ext}"
    path = os.path.join(_folder(category), stored_name)
    size = 0
    with open(path, "wb") as out:
        while chunk := file_storage.stream.read(64 * 1024):
            size += len(chunk)
            if size > max_bytes:
                break
            out.write(chunk)
    try:
        if size > max_bytes:
            raise UploadError(_("Fichier trop volumineux (%(n)d Mo maximum).", n=max_bytes // MB))
        if size == 0:
            raise UploadError(_("Le fichier est vide."))
        mime, signature = FILE_TYPES[ext]
        if isinstance(signature, bytes):
            with open(path, "rb") as f:
                valid = f.read(len(signature)) == signature
        else:
            valid = signature(path)
        if not valid:
            raise UploadError(_("Le contenu du fichier ne correspond pas à son extension (%(ext)s).", ext=ext))
    except UploadError:
        os.remove(path)
        raise

    stored = StoredFile(category=category, original_name=safe_name[:255], stored_name=stored_name,
                        mime_type=mime, size=size, owner_id=owner_id)
    db.session.add(stored)
    return stored


def delete_stored(stored):
    try:
        os.remove(path_of(stored))
    except FileNotFoundError:
        pass
    db.session.delete(stored)


# --- Droits de téléchargement ------------------------------------------------
_ACCESS_RULES = {}


def access_rule(category):
    """Enregistre la fonction (user, stored_file) -> bool qui autorise un téléchargement."""

    def decorator(fn):
        _ACCESS_RULES[category] = fn
        return fn

    return decorator


def can_download(user, stored):
    rule = _ACCESS_RULES.get(stored.category)
    return bool(rule and rule(user, stored))
