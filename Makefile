BASE_PYTHON ?= python
PYTHON := .venv/bin/python
CONDA_ENV_NAME := nf_env



DEFAULT_GOAL := all
SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.PHONY := clean install help download_gtdb-tk venv lint lint-fix help
.SUFFIXES:
.DELETE_ON_ERROR:


hello:
	@echo "Makefile working.."
	@echo "[hello] ok.."


venv: # Create a virtual environment for python analysis
	@if [ ! -d .venv ]; then \
		echo "Environment not found. Creating environment with $(BASE_PYTHON)."; \
		$(BASE_PYTHON) -m venv .venv; \
	fi
	@. .venv/bin/activate && pip install -U pip
	@echo "[venv] ready"

install: venv
	@. .venv/bin/activate && pip install build ruff pytest
	@echo "[install] done"

lint: # Lint code wit ruff
	@. .venv/bin/activate && ruff check .
	@echo "[lint] ok"

lint-fix: # Lint and auto-fix code with ruff
	@. .venv/bin/activate && ruff check . --fix
	@echo "[lint-fix] ok"

conda_env: environment.yml
	@if conda env list | grep "$(CONDA_ENV_NAME)"; then \
		echo "Environment already exisits. Syncing packages..";
		conda env update -n $(CONDA_ENV_NAME) -f environment.yml --prune;\
	else:
		echo "Environment does not exist. Creating the environment from yml file.";
		conda env create -f environment.yml;
	fi
	@echo "Environment is ready. Run conda activate $(CONDA_ENV_NAME) to activate it."
	@echo "[conda_env] ok.."

download_gtdb-tk: # Download the GTDB-TK database. It contains the bacteria and archaea database.
	@echo "Downloading the GTDB-TK database in the detached screen session. This should tak a while.."
	screen -dmS gtdbtk_download bash -c 'bash scripts/download_gtdb-tk.sh > logs/gtdbtk_download.log 2>&1'
	@echo "Check logs/gtdbtk_download.log for progress"
	@echo "[download_gtdb-tk] ok.."