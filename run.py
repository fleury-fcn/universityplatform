"""Point d'entrée : `python run.py` (développement) ou `gunicorn run:app` (production)."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _use_project_python():
    """Lancé avec un Python sans les dépendances (bouton « Run » de l'éditeur, python3 du système) :
    on relance automatiquement le script avec l'environnement du projet (.venv)."""
    try:
        import flask  # noqa: F401
        return
    except ModuleNotFoundError:
        pass
    if VENV_PYTHON.exists() and Path(sys.prefix).resolve() != VENV.resolve():
        import subprocess

        print(f"Relance avec l'environnement du projet : {VENV_PYTHON}", flush=True)
        # Sous-processus (et non os.execv) : fonctionne aussi depuis le débogueur de l'éditeur.
        try:
            code = subprocess.call([str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]], cwd=ROOT)
        except KeyboardInterrupt:
            code = 0
        sys.exit(code)
    sys.exit(
        "Les dépendances ne sont pas installées pour ce Python.\n"
        "Installez-les une fois avec :  make install\n"
        "(ou : python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt)"
    )


if __name__ == "__main__":
    _use_project_python()

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    # 5001 et non 5000 : sur macOS, le port 5000 est occupé par le récepteur AirPlay.
    port = int(os.environ.get("PORT", "5001"))
    print(f"Application disponible sur http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port)
