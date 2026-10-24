"""Recherche tolérante dans la FAQ : sans accents, sans mots vides, par recouvrement de mots."""
import re
import unicodedata

STOPWORDS = set("""
a au aux avec ce ces comment dans de des du elle en est et il je la le les leur mais me mes mon ne
on ou par pas pour qu que qui quoi sa se ses son sur ta te tes ton tu un une vos votre vous y
est-ce quand quel quelle quels quelles puis peut faire fait
""".split())


def normalize(text):
    text = unicodedata.normalize("NFKD", (text or "").lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return [w for w in re.findall(r"[a-z0-9]+", text) if len(w) > 1 and w not in STOPWORDS]


def _stem(word):
    # Racine grossière : suffit pour rapprocher « inscrire / inscription », « note / notes ».
    for suffix in ("ations", "ation", "ements", "ement", "ions", "ion", "ees", "ee", "es", "er", "s", "e"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def rank(entries, query, limit=5):
    terms = {_stem(w) for w in normalize(query)}
    if not terms:
        return []
    scored = []
    for entry in entries:
        question = {_stem(w) for w in normalize(entry.question + " " + (entry.keywords or ""))}
        answer = {_stem(w) for w in normalize(entry.answer)}
        score = 3 * len(terms & question) + len(terms & answer)
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda item: (-item[0], item[1].position))
    return [entry for _, entry in scored[:limit]]
