#!/bin/bash
# Stage 2: Binning and Taxonomy from Assembly Input
# Run after Stage 1 assemblies and work cleanup

set -euo pipefail

PROJECT_ROOT="/home/inf-21-2024/nbis"
STAGE2_CONFIG="${PROJECT_ROOT}/config/stage2_binning.config"
RUN_NAME="kf_top_stage2_$(date +%Y%m%d_%H%M%S)"
LOGFILE="${PROJECT_ROOT}/logs/${RUN_NAME}.log"
mkdir -p "${PROJECT_ROOT}/logs"

echo "======================================"
echo "STAGE 2: Binning → Taxonomy"
echo "======================================"
echo "Run name: ${RUN_NAME}"
echo "Config: ${STAGE2_CONFIG}"
echo "Log: ${LOGFILE}"
echo ""

# Check assembly samplesheet exists
ASSEMBLY_SHEET="${PROJECT_ROOT}/samplesheet/kf_top/kf_top_assembly_samplesheet.csv"
if [[ ! -f "${ASSEMBLY_SHEET}" ]]; then
    echo "ERROR: Assembly samplesheet not found!"
    echo "Create it with: python scripts/create_assembly_samplesheet.py"
    exit 1
fi

export SINGULARITY_TMPDIR=/home/inf-21-2024/nbis/.singularity_tmp
export APPTAINER_TMPDIR=/home/inf-21-2024/nbis/.singularity_tmp

nextflow run nf-core/mag \
    -r 5.0.0 \
    -profile singularity \
    -c "${STAGE2_CONFIG}" \
    --run_name "${RUN_NAME}" \
    -resume \
    2>&1 | tee "${LOGFILE}"

echo ""
echo "======================================"
echo "STAGE 2 COMPLETE!"
echo "======================================"
echo "Taxonomy results: ${PROJECT_ROOT}/results/Taxonomy/GTDB-Tk/"
echo "Bin summary: ${PROJECT_ROOT}/results/GenomeBinning/bin_summary.tsv"
