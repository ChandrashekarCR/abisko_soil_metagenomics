BASE_PYTHON ?= python
VENV := .venv
PYTHON := $(VENV)/bin/python
CONDA_ENV_NAME := nf_env
PIP := $(VENV)/bin/pip

DEFAULT_GOAL := all
SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.PHONY := clean install help download_gtdb-tk venv lint lint-fix build-image help
.SUFFIXES:
.DELETE_ON_ERROR:


hello:
	@echo "Makefile working.."
	@echo "[hello] ok.."

help: # Help file to understand the Makefile
	@echo "Available Makefile targets:"
	@echo "hello - Test if the Makefile is working"
	@echo "build-image - Build the Singularity/Apptainer .sif image"
	@echo "venv - Create a Python virtual environment in .venv"
	@echo "install - Install Python dev tools (build, ruff, pytest) in .venv"
	@echo "lint - Lint code with ruff"
	@echo "lint-fix - Lint and auto-fix code with ruff"
	@echo "conda_env - Create or update the Conda environment from environment.yml"
	@echo "download_gtdb-tk - Download the GTDB-TK database in a detached screen session"


clean: # Clean all the files
	@find . -name ".nextflow.log*" -exec rm -rf {} +
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "[clean] ok"

build-image: # Build a .sif file for better reproducibility
	@echo "Checking if the .sif file exisits.."
	@if [ -f *.sif ]; then \
		echo "Image already exists..";\
	else \
		if [ ! -f Singularity ]; then \
			echo "Singularity file does not exist..";\
			exit 1;\
		fi;\
		echo "Building image using the Singularity file..";\
		apptainer build abisko_pipeline.sif Singularity;\
	fi
	@echo "[build-image] done"

venv: # Create a virtual environment for python analysis
	@if [ ! -d $(VENV) ]; then \
		echo "Environment not found. Creating environment with $(BASE_PYTHON)."; \
		$(BASE_PYTHON) -m venv $(VENV); \
	fi
	@. .venv/bin/activate && $(PIP) install -U pip
	@echo "[venv] ready"

install: venv
	@echo "Installing core dependencies..."
	@$(PIP) install -e .
	@echo "[install] ok"

install-dev: venv
	@echo "Installing development dependencies..."
	@$(PIP) install -e ".[dev]"
	@echo "[install-dev] ok"

lint: # Linting python scripts
	@$(PYTHON) -m ruff check . || (echo '[lint] ruff failed' >&2; exit 1)
	@echo "[lint] ok"	

lint-fix: # Lint and auto-fix code with ruff
	@echo "Organizing imports with ruff.."
	@$(PYTHON) -m ruff check --fix src/ tests/ || (echo '[format] ruff import sorting failed' >&2; exit 1)
	@$(PYTHON) -m ruff format src/ tests/ || (echo '[format] ruff format failed' >&2; exit 1)
	@echo "[lint-fix] ok"

test: # Run pytests for script
	@echo "Running core tests.."
	@. .venv/bin/activate && pytest tests/
	@echo "[test] ok"

conda_env: environment.yml
	@if conda env list | grep "$(CONDA_ENV_NAME)"; then \
		echo "Environment already exisits. Syncing packages..";
		conda env update -n $(CONDA_ENV_NAME) -f environment.yml --prune;\
	else \
		echo "Environment does not exist. Creating the environment from yml file.";
		conda env create -f environment.yml;
	fi
	@echo "Environment is ready. Run conda activate $(CONDA_ENV_NAME) to activate it."
	@echo "[conda_env] ok.."

download_gtdb-tk: # Download the GTDB-TK database. It contains the bacteria and archaea database.
	@echo "Downloading the GTDB-TK database in the detached screen session. This should tak a while.."
	screen -dmS gtdbtk_download bash -c 'bash src/download_gtdb-tk.sh > logs/gtdbtk_download.log 2>&1'
	@echo "Check logs/gtdbtk_download.log for progress"
	@echo "[download_gtdb-tk] ok.."