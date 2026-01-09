BASE_PYTHON ?= python
PYTHON := .venv/bin/python
CONDA_ENV_NAME := nf_env



DEFAULT_GOAL := all
SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.PHONY := clean help download venv lint help
.SUFFIXES:
.DELETE_ON_ERROR:


hello:
	@echo "Makefile working.."
	@echo "[hello] read.."


venv: # Create a virtual environment for python analysis
	@if [ ! -d .venv ]; then \
		echo "Environment not found. Creating environment with $(BASE_PYTHON)."; \
		$(BASE_PYTHON) -m venv .venv; \
	fi
	@. .venv/bin/activate && pip install -U pip
	@echo "[venv] ready"


conda_env: environment.yml
	@if conda env list | grep "$(CONDA_ENV_NAME)"; then \
		echo "Environment already exisits. Syncing packages..";
		conda env update -n $(CONDA_ENV_NAME) -f environment.yml --prune;\
	else:
		echo "Environment does not exist. Creating the environment from yml file.";
		conda env create -f environment.yml;
	fi
	@echo "Environment is ready. Run conda activate $(CONDA_ENV_NAME) to activate it."
	@echo "[conda_env] ok"