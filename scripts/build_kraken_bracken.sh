#!/usr/bin/bash

set -euo pipefail

CONDA_ENV_NAME="nf_env"
# Get the directory of the project and scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

printf '%.0s=' {1..40}
printf '\n'
echo "Setting up kraken and bracken databases.."
printf '%.0s=' {1..40}
printf '\n'

# 1. Installation of dependencies
echo "[1/6] Installing dependencies" 
if conda env list | grep -q "$CONDA_ENV_NAME"; then \
    # Activate conda environment
    eval "$(conda shell.bash hook)" # Attach the terminal to the conda environemt. This step is crucial for the script to run.
    conda activate "$CONDA_ENV_NAME"

    # Check if kraken and bracken are installed
    if ! command -v kraken2 >/dev/null 2>&1 || ! command -v bracken >/dev/null 2>&1; then \
        echo "Error: kraken and/or bracken are not installed in the $CONDA_ENV_NAME environment."
        echo "Please install via the make conda_env command and re-run the script."
        exit 0
    fi

    echo "kraken2 and bracken are installed."
    echo "$(which kraken2)"
    echo "$(which bracken)"
else
    echo "Conda environemt $CONDA_ENV_NAME does not exist."
    echo "Please install via the make conda_env command and re-run the script."
    exit 0

fi

# Build Kraken2 database
echo "[2/6] Building Kraken2 database (bacteria + archaea)"
mkdir -p $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db

if [ ! -d $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db/taxonomy ]; then \
    # Download the database
    echo "Downloading the taxonomy database";
    screen -dmS kraken2_taxonomy bash -c "eval \"\$(conda shell.bash hook)\" && conda activate $CONDA_ENV_NAME && kraken2-build --download-taxonomy --db $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db > $PROJECT_ROOT/kraken2_dbs/taxonomy_download.log 2>&1";
    echo "Taxonomy download started in screen session 'kraken2_dbs'. Use screen -r kraken2_dbs to attach and monitor.";
else \
    echo "Taxonomy directory already exists.";
fi

echo "Downloading the library for bacteria and archaea.."
screen -dmS kraken2_build bash -c "
    eval \"\$(conda shell.bash hook)\"
    conda activate $CONDA_ENV_NAME 
    kraken2-build --download-library bacteria \
    --db $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db \
    --threads 32 > $PROJECT_ROOT/kraken2_dbs/build.log 2>&1"
