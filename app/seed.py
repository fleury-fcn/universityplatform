"""Données de démonstration.

Tout ce qui est créé ici est marqué DEMO (champ is_demo) et listé dans
DONNEES_A_COMPLETER.md. Les seules informations ISTA reprises sont celles qui
figuraient déjà dans l'ancien code (départements, filières, clubs).
"""
from app.extensions import db


def run():
    db.session.commit()
