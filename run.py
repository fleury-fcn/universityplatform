"""Point d'entrée : `python run.py` (développement) ou `gunicorn run:app` (production)."""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # 5001 et non 5000 : sur macOS, le port 5000 est occupé par le récepteur AirPlay.
    port = int(os.environ.get("PORT", "5001"))
    print(f"Application disponible sur http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port)
