"""Comptes utilisateurs."""
from datetime import timedelta

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.security import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER
from app.extensions import db

from . import TimestampMixin, utcnow

MAX_FAILED_LOGINS = 5
LOCK_DURATION = timedelta(minutes=15)
# Calculé une seule fois : sert à garder un temps de réponse constant si l'identifiant n'existe pas.
_DUMMY_HASH = generate_password_hash("mot-de-passe-factice")


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    matricule = db.Column(db.String(32), unique=True, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT)
    password_hash = db.Column(db.String(255), nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey("promotions.id"))
    locale = db.Column(db.String(5))

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    # Incrémenté à chaque changement de mot de passe : invalide les autres sessions.
    session_version = db.Column(db.Integer, nullable=False, default=1)
    failed_logins = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    is_demo = db.Column(db.Boolean, nullable=False, default=False)

    promotion = db.relationship("Promotion", back_populates="students")

    # --- Identité -----------------------------------------------------------
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_student(self):
        return self.role == ROLE_STUDENT

    @property
    def is_teacher(self):
        return self.role == ROLE_TEACHER

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_staff(self):
        return self.role in (ROLE_TEACHER, ROLE_ADMIN)

    def get_id(self):
        return f"{self.id}:{self.session_version}"

    # --- Mot de passe -------------------------------------------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method=current_app.config["PASSWORD_HASH_METHOD"])
        self.session_version = (self.session_version or 0) + 1

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def burn_password_check(password):
        check_password_hash(_DUMMY_HASH, password)

    # --- Verrouillage après échecs ------------------------------------------
    @property
    def is_locked(self):
        return self.locked_until is not None and self.locked_until > utcnow()

    def register_failed_login(self):
        self.failed_logins = (self.failed_logins or 0) + 1
        if self.failed_logins >= MAX_FAILED_LOGINS:
            self.locked_until = utcnow() + LOCK_DURATION
            self.failed_logins = 0

    def register_successful_login(self):
        self.failed_logins = 0
        self.locked_until = None
        self.last_login_at = utcnow()

    @classmethod
    def find_by_login(cls, identifier):
        identifier = (identifier or "").strip()
        if not identifier:
            return None
        return cls.query.filter(
            db.or_(
                cls.username == identifier.lower(),
                cls.email == identifier.lower(),
                cls.matricule == identifier.upper(),
            )
        ).first()

    def __repr__(self):
        return f"<User {self.username}>"
