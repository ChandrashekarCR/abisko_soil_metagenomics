BASE_PYTHON ?= python
PYTHON := .venv/bin/python


DEFAULT_GOAL := all
SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.PHONY := clean help download venv lint help
.SUFFIXES:
.DELETE_ON_ERROR:


venv: # Create a virtual environment for python analysis
	@if [ ! -d .venv ]; then \
		echo "Environment not found. Creating environment with $(BASE_PYTHON)."; \
		$(BASE_PYTHON) -m venv .venv; \
	fi
	@. .venv/bin/activate && pip install -U pip
	@echo "[venv] ready"