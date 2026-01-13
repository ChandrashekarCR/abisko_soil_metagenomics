#!/usr/bin/bash

set -euo pipefail

CONDA_ENV_NAME="nf_env"
# Get the directory of the project and scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Global variables
DOWLOAD_DIR="$PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db"
DB_DIR="$PROJECT_ROOT/kraken2_dbs"

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

if [ ! -d "$PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db/taxonomy" ]; then \
    # Download the database
    echo "Downloading the taxonomy database";
    screen -dmS kraken2_taxonomy bash -c "eval \"\$(conda shell.bash hook)\"  
        conda activate $CONDA_ENV_NAME 
        kraken2-build --download-taxonomy \
        --db $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db > $PROJECT_ROOT/kraken2_dbs/taxonomy_download.log 2>&1";
    echo "Taxonomy download started in screen session 'kraken2_dbs'. Use screen -r kraken2_dbs to attach and monitor.";
else \
    echo "Taxonomy directory already exists.";
fi

if [ ! -d "$PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db/library/archaea" ]; then 
    echo "Archaea libraries are not present.."
    echo "Downloading the library for archaea.."
    screen -dmS kraken2_library_archaea bash -c "
        eval \"\$(conda shell.bash hook)\"
        conda activate $CONDA_ENV_NAME 
        kraken2-build --download-library archaea \
        --db $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db \
        --threads 32 > $PROJECT_ROOT/kraken2_dbs/archaea_library.log 2>&1"
else \
    echo "Archaea library is already present.."
fi
if [ ! -d "$PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db/library/bacteria" ]; then
    echo "Bacteria libraries are not present.."
    echo "Downloading the library for bacteria.."
    screen -dmS kraken2_library_bacteria bash -c "
        eval \"\$(conda shell.bash hook)\"
        conda activate $CONDA_ENV_NAME
        kraken2-build --download-library bacteria \
        --db $PROJECT_ROOT/kraken2_dbs/bacteria_archaea_db >$PROJECT_ROOT/kraken2_dbs/bacteria_library.log 2>&1"
else \
    echo "Bacteria library is already present.."
fi


# Building only the archae database
# Create database directories
if [ ! -d $PROJECT_ROOT/archaea ]; then 
    echo "Database does not exist. Creating .."
    mkdir -p $DB_DIR/archaea_db
else 
    echo "Database already exists."
fi

if [  -f $DB_DIR/archaea_db/hash.k2d ]; then
        echo "Combined database already exists. Skipping.."
else
    # Copy taxonomy to combined database
    echo "Step[1 / 4] Copying taxonomy.."
    #cp -r $DOWLOAD_DIR/taxonomy $DB_DIR/archaea_db

    echo "Step[2 / 4] Copying archaea libraries"
    cp -r $DOWLOAD_DIR/library/archaea $DB_DIR/archaea_db/library

    echo "Stepp[3 / 4] Building the archaea database"
    echo "This will take mostly 2-3 hours. Running in the background."

    screen -dmS kraken2_build_archaea bash -c "
    eval \"\$(conda shell.bash hook)\"
    conda activate $CONDA_ENV_NAME
    kraken2-build --build \
        --db $DB_DIR/archaea_db \
        --threads 16 \
        > $DB_DIR/archaea_db_build.log 2>&1

    # Clean up after build
    kraken2-build --clean --db $DB_DIR/archaea_db

    echo 'Archaea database build completed at \$(date)' >> $DB_DIR/archaea_db_build.log
    "
    
    echo "Archaea database build started in screen session 'kraken2_build_archaea'"
    echo "Monitor with: screen -r kraken2_build_archaea"
    echo "Log file: $DB_DIR/archaea_only_build.log"
fi

echo "[6/6] All steps completed."