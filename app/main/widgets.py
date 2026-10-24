"""Blocs de l'accueil : chaque fonctionnalité enregistre le sien."""
_WIDGETS = []


def home_widget(order):
    """Décore une fonction (user) -> (gabarit, contexte) | None affichée sur l'accueil."""

    def decorator(fn):
        _WIDGETS.append((order, fn))
        return fn

    return decorator


def collect(user):
    widgets = []
    for _, fn in sorted(_WIDGETS, key=lambda item: item[0]):
        result = fn(user)
        if result:
            widgets.append(result)
    return widgets
