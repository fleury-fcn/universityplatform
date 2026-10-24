"""Création de comptes (formulaire et import CSV)."""
import csv
import io
import secrets

from flask_babel import gettext as _

from app.core.security import ROLES, ROLE_STUDENT
from app.extensions import db
from app.models import Promotion, User

_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"  # sans caractères ambigus (l, 1, o, 0, i)

CSV_COLUMNS = ["matricule", "prenom", "nom", "email", "promotion", "role"]


def generate_temp_password():
    raw = "".join(secrets.choice(_ALPHABET) for _ in range(12))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"


def normalize_identity(username, matricule, email):
    matricule = matricule.strip().upper() if matricule else None
    username = (username or matricule or "").strip().lower()
    email = email.strip().lower() if email else None
    return username, matricule, email


def find_conflict(username, matricule, email, exclude_id=None):
    """Retourne un message d'erreur si l'identifiant, le matricule ou l'e-mail est déjà pris."""
    checks = [
        (User.username == username, _("L'identifiant « %(v)s » est déjà utilisé.", v=username)),
    ]
    if matricule:
        checks.append((User.matricule == matricule, _("Le matricule « %(v)s » est déjà utilisé.", v=matricule)))
    if email:
        checks.append((User.email == email, _("L'e-mail « %(v)s » est déjà utilisé.", v=email)))
    for condition, message in checks:
        query = User.query.filter(condition)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        if query.first():
            return message
    return None


def create_user(*, first_name, last_name, role, username=None, matricule=None, email=None,
                promotion_id=None, is_active=True):
    """Crée un compte avec un mot de passe provisoire. Retourne (user, mot_de_passe)."""
    username, matricule, email = normalize_identity(username, matricule, email)
    password = generate_temp_password()
    user = User(
        username=username,
        matricule=matricule,
        email=email,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        role=role,
        promotion_id=promotion_id if role == ROLE_STUDENT else None,
        is_active=is_active,
        must_change_password=True,
    )
    user.set_password(password)
    db.session.add(user)
    return user, password


def import_users_csv(raw_bytes):
    """Importe des comptes depuis un CSV. Tout ou rien : retourne (créés, erreurs)."""
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1")
    try:
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=";,")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = [h.strip().lower() for h in (reader.fieldnames or [])]
    missing = [c for c in ("prenom", "nom") if c not in headers]
    if missing:
        return [], [_("Colonnes manquantes : %(cols)s", cols=", ".join(missing))]

    promotions = {p.code.upper(): p.id for p in Promotion.query.all()}
    created, errors, seen = [], [], set()
    for line_no, row in enumerate(reader, start=2):
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        if not any(row.values()):
            continue
        role = (row.get("role") or ROLE_STUDENT).lower()
        promotion_code = row.get("promotion", "").upper()
        username, matricule, email = normalize_identity(None, row.get("matricule"), row.get("email"))
        problem = None
        if role not in ROLES:
            problem = _("rôle inconnu « %(v)s »", v=role)
        elif not row.get("prenom") or not row.get("nom"):
            problem = _("prénom et nom obligatoires")
        elif role == ROLE_STUDENT and not matricule:
            problem = _("matricule obligatoire pour un étudiant")
        elif not username:
            problem = _("matricule obligatoire")
        elif promotion_code and promotion_code not in promotions:
            problem = _("promotion inconnue « %(v)s »", v=promotion_code)
        elif username in seen:
            problem = _("doublon dans le fichier")
        else:
            problem = find_conflict(username, matricule, email)
        if problem:
            errors.append(_("Ligne %(n)d : %(problem)s", n=line_no, problem=problem))
            continue
        seen.add(username)
        user, password = create_user(
            first_name=row["prenom"], last_name=row["nom"], role=role, matricule=matricule,
            email=email, promotion_id=promotions.get(promotion_code),
        )
        created.append((user, password))

    if errors:
        db.session.rollback()
        return [], errors
    db.session.commit()
    return created, []


def _csv_safe(value):
    """Neutralise les formules (=, +, -, @) à l'ouverture dans un tableur."""
    return "'" + value if value[:1] in ("=", "+", "-", "@") else value


def credentials_csv(created):
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow(["identifiant", "matricule", "prenom", "nom", "mot_de_passe_provisoire"])
    for user, password in created:
        writer.writerow([_csv_safe(v) for v in (user.username, user.matricule or "", user.first_name,
                                               user.last_name, password)])
    return "﻿" + out.getvalue()
