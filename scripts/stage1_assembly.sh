#!/bin/bash
# Stage 1: QC and Assembly only
# Saves storage by skipping downstream steps

set -euo pipefail

PROJECT_ROOT="/home/inf-21-2024/nbis"
CUSTOM_CONFIG="${PROJECT_ROOT}/config/custom_default.config"
RUN_NAME="kf_top_stage1_$(date +%Y%m%d_%H%M%S)"
LOGFILE="${PROJECT_ROOT}/logs/${RUN_NAME}.log"
mkdir -p "${PROJECT_ROOT}/logs"

echo "======================================"
echo "STAGE 1: QC → Assembly"
echo "======================================"
echo "Run name: ${RUN_NAME}"
echo "Config: ${CUSTOM_CONFIG}"
echo "Log: ${LOGFILE}"
echo ""

export SINGULARITY_TMPDIR=/home/inf-21-2024/nbis/.singularity_tmp
export APPTAINER_TMPDIR=/home/inf-21-2024/nbis/.singularity_tmp

nextflow run nf-core/mag \
    -r 5.0.0 \
    -profile singularity \
    -c "${CUSTOM_CONFIG}" \
    --run_name "${RUN_NAME}" \
    -resume \
    2>&1 | tee "${LOGFILE}"

echo ""
echo "======================================"
echo "STAGE 1 COMPLETE!"
echo "======================================"
echo "Assemblies saved in: ${PROJECT_ROOT}/results/Assembly/"
echo ""
echo "Next steps:"
echo "1. Create assembly samplesheet:"
echo "   python scripts/create_assembly_samplesheet.py"
echo ""
echo "2. Clean work directory to free space:"
echo "   rm -rf work/"
echo "   du -sh results/  # Check results size"
echo ""
echo "3. Run Stage 2 (binning & taxonomy):"
echo "   bash scripts/stage2_binning.sh"
