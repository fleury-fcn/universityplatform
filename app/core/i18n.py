"""Compilation des catalogues de traduction au démarrage (les .mo ne sont pas versionnés)."""
import os
import tempfile
from pathlib import Path

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po


def compile_catalogs(translations_dir, force=False):
    for po_path in Path(translations_dir).glob("*/LC_MESSAGES/messages.po"):
        mo_path = po_path.with_suffix(".mo")
        if not force and mo_path.exists() and mo_path.stat().st_mtime >= po_path.stat().st_mtime:
            continue
        with po_path.open("rb") as f:
            catalog = read_po(f)
        # Écriture atomique : plusieurs processus peuvent démarrer en même temps.
        fd, tmp = tempfile.mkstemp(dir=mo_path.parent, suffix=".mo")
        with os.fdopen(fd, "wb") as f:
            write_mo(f, catalog, use_fuzzy=False)
        os.replace(tmp, mo_path)
