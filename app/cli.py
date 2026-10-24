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
