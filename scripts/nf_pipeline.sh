#!/bin/bash
set -euo pipefail

PROJECT_ROOT="/home/inf-21-2024/nbis"
CUSTOM_CONFIG="${PROJECT_ROOT}/config/custom.config"
WORK_DIR="${PROJECT_ROOT}/work"
OUTDIR="${PROJECT_ROOT}/results"

RUN_NAME="abisko_soil_$(date +%Y%m%d_%H%M%S)"   
LOGFILE="${PROJECT_ROOT}/logs/${RUN_NAME}.log"
mkdir -p ${PROJECT_ROOT}/logs

# Verify GTDB-Tk database is extracted
if [ ! -d "/home/inf-21-2024/nbis/databases/gtdb-tk/gtdbtk_r220_data/" ]; then
    echo "ERROR: GTDB-Tk database not properly extracted!"
    echo "Expected structure: gtdbtk_r220_data/fastani/, gtdbtk_r220_data/markers/, etc."
    exit 1
fi

echo "Starting nf-core/mag pipeline..."

nextflow run nf-core/mag \
    -r 5.0.0 \
    -profile singularity \
    -c "${CUSTOM_CONFIG}" \
    -work-dir "${WORK_DIR}" \
    --run_name "${RUN_NAME}"\
    -resume \
    2>&1 | tee "${LOGFILE}"

echo "Pipeline started successfully!"