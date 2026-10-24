# Lancement en une commande : `make dev`
VENV ?= .venv
PY := $(VENV)/bin/python
export FLASK_APP := run.py
HOST ?= 127.0.0.1
PORT ?= 5000

.PHONY: dev install db seed run test translations clean

dev: seed run  ## Installe, prépare la base, charge la démo et lance l'application

$(VENV)/.installed: requirements.txt requirements-dev.txt
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements-dev.txt
	touch $@

install: $(VENV)/.installed

db: install
	$(PY) -m flask db upgrade

seed: db
	$(PY) -m flask seed-demo

run: install
	$(PY) -m flask run --host $(HOST) --port $(PORT)

test: install
	$(PY) -m pytest

translations: install
	$(PY) -m flask translate update

clean:
	rm -rf $(VENV) .pytest_cache
