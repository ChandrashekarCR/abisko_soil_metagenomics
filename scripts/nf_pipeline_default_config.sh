#!/bin/bash

# Optimized nf-core/mag pipeline for paired short reads
# Hardware: 250 CPUs, 2TB RAM
# Goal: Taxonomy classification with microbial abundance
# ALL PARAMETERS ARE NOW IN THE CONFIG FILE

set -euo pipefail

PROJECT_ROOT="/home/inf-21-2024/nbis"
CUSTOM_CONFIG="${PROJECT_ROOT}/config/custom_default.config"
RUN_NAME="abisko_soil_$(date +%Y%m%d_%H%M%S)"   
LOGFILE="${PROJECT_ROOT}/logs/${RUN_NAME}.log"
mkdir -p "${PROJECT_ROOT}/logs"

echo "Starting nf-core/mag pipeline with clean config approach..."
echo "Run name: ${RUN_NAME}"
echo "Config file: ${CUSTOM_CONFIG}"
echo "Log file: ${LOGFILE}"

nextflow run nf-core/mag \
    -r 5.0.0 \
    -profile singularity \
    -c "${CUSTOM_CONFIG}" \
    --run_name "${RUN_NAME}" \
    -resume \
    2>&1 | tee "${LOGFILE}"

echo "Pipeline completed successfully!"