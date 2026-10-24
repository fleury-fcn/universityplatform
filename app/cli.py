"""Commandes d'administration : flask seed-demo, flask translate ..."""
from pathlib import Path

import click
from babel.messages.frontend import CommandLineInterface

from .core.i18n import compile_catalogs

TRANSLATIONS = Path(__file__).parent / "translations"
POT = TRANSLATIONS / "messages.pot"


def _pybabel(*args):
    CommandLineInterface().run(["pybabel", "-q", *args])


def register_cli(app):
    @app.cli.command("seed-demo")
    def seed_demo():
        """Charge les données de démonstration (marquées DEMO). Sans effet si déjà chargées."""
        from .seed import run

        run()
        click.echo("Données de démonstration chargées.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt="Identifiant")
    @click.option("--first-name", prompt="Prénom")
    @click.option("--last-name", prompt="Nom")
    @click.password_option("--password", prompt="Mot de passe")
    def create_admin(username, first_name, last_name, password):
        """Crée un compte administrateur (premier déploiement)."""
        from .core.security import ROLE_ADMIN
        from .extensions import db
        from .models import User

        username = username.strip().lower()
        if User.query.filter_by(username=username).first():
            raise click.ClickException("Cet identifiant existe déjà.")
        if len(password) < 8 or password.isdigit():
            raise click.ClickException("Mot de passe trop faible (8 caractères minimum, pas uniquement des chiffres).")
        user = User(username=username, first_name=first_name.strip(), last_name=last_name.strip(), role=ROLE_ADMIN)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Administrateur « {username} » créé.")

    @app.cli.command("push-keys")
    def push_keys():
        """Génère une paire de clés VAPID pour les notifications push."""
        import base64

        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        def b64(data):
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

        key = ec.generate_private_key(ec.SECP256R1())
        public = key.public_key().public_bytes(serialization.Encoding.X962,
                                               serialization.PublicFormat.UncompressedPoint)
        click.echo("Ajoutez ces lignes à votre fichier .env (ne les publiez jamais) :")
        click.echo(f"VAPID_PUBLIC_KEY={b64(public)}")
        click.echo(f"VAPID_PRIVATE_KEY={b64(key.private_numbers().private_value.to_bytes(32, 'big'))}")

    @app.cli.group()
    def translate():
        """Gestion des traductions (fr par défaut, en, rn)."""

    @translate.command()
    def update():
        """Extrait les textes et met à jour les catalogues .po."""
        root = Path(__file__).parent.parent
        _pybabel("extract", "-F", str(root / "babel.cfg"), "-k", "_l", "-o", str(POT), str(root / "app"))
        for lang in app.config["LANGUAGES"]:
            if lang == app.config["BABEL_DEFAULT_LOCALE"]:
                continue
            po = TRANSLATIONS / lang / "LC_MESSAGES" / "messages.po"
            cmd = "update" if po.exists() else "init"
            _pybabel(cmd, "-i", str(POT), "-d", str(TRANSLATIONS), "-l", lang)

    @translate.command()
    def compile():
        """Compile les catalogues .po en .mo (fait automatiquement au lancement)."""
        compile_catalogs(TRANSLATIONS, force=True)
