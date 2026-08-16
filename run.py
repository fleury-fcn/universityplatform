from app import create_app
import os
import socket
import threading
import webbrowser
import sys

app = create_app()


def _is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', port))
        except OSError:
            return False
    return True


def _pick_available_port(preferred_port: int) -> int:
    """Sélectionne uniquement le port demandé pour éviter les changements dynamiques."""
    if _is_port_free(preferred_port):
        return preferred_port
    raise RuntimeError(f"Le port {preferred_port} est indisponible. Libérez-le puis relancez l'application.")


def _schedule_browser_open(url: str, delay: float = 1.0) -> None:
    def _open():
        try:
            webbrowser.open(url, new=2)
        except webbrowser.Error as err:
            print(f"Impossible d'ouvrir le navigateur automatiquement: {err}")

    threading.Timer(delay, _open).start()


if __name__ == '__main__':
    try:
        desired_port = int(os.environ.get('PORT', 5002))
        selected_port = int(os.environ.get('APP_SELECTED_PORT', desired_port))
        if 'APP_SELECTED_PORT' not in os.environ:
            selected_port = _pick_available_port(desired_port)
            os.environ['APP_SELECTED_PORT'] = str(selected_port)
        url = f"http://127.0.0.1:{selected_port}"
        print(f"Application disponible sur {url}")
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            _schedule_browser_open(url)
        app.run(host='0.0.0.0', port=selected_port, use_reloader=True)
    except Exception as err:
        print(f"Erreur lors du demarrage du serveur: {err}")
        sys.exit(1)

