"""Utilities for harmonizing ISTA academic structures."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set
import unicodedata

# Canonical department choices displayed across the UI
DEPARTMENT_CHOICES: List[tuple[str, str]] = [
    ("ACTU", "Actuariat"),
    ("GENSTAT", "Genie Statistique"),
    ("PROBA", "Probabilites & Statistique"),
]

# Canonical master parcours choices
MASTER_PARCOURS_CHOICES: List[tuple[str, str]] = [
    ("MACTU", "Master Actuariat & Finance"),
    ("MSAID", "Master Statistique Appliquee & Informatique Decisionnelle"),
    ("MMSP", "Master Modelisation Statistique & Probabilite"),
]

# Mapping between parcours and their parent departments
PARCOURS_TO_DEPARTMENT: Dict[str, str] = {
    "MACTU": "ACTU",
    "MSAID": "GENSTAT",
    "MMSP": "PROBA",
}

# Alias maps (all uppercase/ascii) used for normalization
_DEPARTMENT_ALIAS_MAP: Dict[str, Set[str]] = {
    "ACTU": {"ACTU", "ACTUARIAT"},
    "GENSTAT": {"GENSTAT", "GENIE", "GENIE STATISTIQUE"},
    "PROBA": {
        "PROBA",
        "PROBABILITE",
        "PROBABILITES",
        "PROBABILITE ET STATISTIQUE",
        "PROBABILITES ET STATISTIQUE",
        "PROBASTATE",
    },
}

_PARCOURS_ALIAS_MAP: Dict[str, Set[str]] = {
    "MACTU": {"MACTU", "AF", "ACTUARIAT ET FINANCE"},
    "MSAID": {"MSAID", "SAID", "STATISTIQUE APPLIQUEE ET INFORMATIQUE DECISIONNELLE"},
    "MMSP": {"MMSP", "PSM", "PROBABILITE STATISTIQUE ET MODELISATION"},
}


def _slug(value: Optional[str]) -> str:
    """Return an uppercase ASCII slug for comparisons."""
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value.strip())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_value.upper()


def _normalize(value: Optional[str], alias_map: Dict[str, Set[str]]) -> Optional[str]:
    slug = _slug(value)
    if not slug:
        return None
    for code, aliases in alias_map.items():
        if slug in aliases:
            return code
    return slug


def normalize_department(value: Optional[str]) -> Optional[str]:
    """Normalize any department label/code to the canonical ACTU/GENSTAT/PROBA form."""
    return _normalize(value, _DEPARTMENT_ALIAS_MAP)


def normalize_parcours(value: Optional[str]) -> Optional[str]:
    """Normalize any parcours label/code to MACTU/MSAID/MMSP."""
    return _normalize(value, _PARCOURS_ALIAS_MAP)


def get_department_variants(value: Optional[str]) -> Set[str]:
    """Return all known variants for the provided department value (including canonical)."""
    normalized = normalize_department(value)
    if not normalized:
        return set()
    return set(_DEPARTMENT_ALIAS_MAP.get(normalized, {normalized}))


def get_parcours_variants(value: Optional[str]) -> Set[str]:
    """Return all known variants for the provided parcours value."""
    normalized = normalize_parcours(value)
    if not normalized:
        return set()
    return set(_PARCOURS_ALIAS_MAP.get(normalized, {normalized}))


def get_department_from_parcours(parcours_code: Optional[str]) -> Optional[str]:
    """Infer the parent department from a parcours code if possible."""
    normalized = normalize_parcours(parcours_code)
    if not normalized:
        return None
    return PARCOURS_TO_DEPARTMENT.get(normalized)


def get_department_label(code: Optional[str]) -> str:
    """Human label for a canonical department code."""
    normalized = normalize_department(code)
    for dept_code, label in DEPARTMENT_CHOICES:
        if dept_code == normalized:
            return label
    return code or ""


def get_parcours_label(code: Optional[str]) -> str:
    """Human label for a canonical parcours code."""
    normalized = normalize_parcours(code)
    for parcours_code, label in MASTER_PARCOURS_CHOICES:
        if parcours_code == normalized:
            return label
    return code or ""
