# Abisko Soil Metagenomics (nf-core/mag + downstream analysis)

This repository contains:

1) A reproducible way to run the nf-core/mag pipeline on Abisko soil metagenomes (with a custom Nextflow config and a Singularity/Apptainer image).
2) Small Python utilities (in `src/`) for post-processing GTDB-Tk output, merging per-sample TSVs, generating taxonomic abundance plots, and producing comparative taxonomy reports.

## What’s in here

### Pipeline / reproducibility

- **nf-core/mag runner**: `src/nf_pipeline_default_config.sh` (uses `config/custom_default.config`)
- **Container image**: `abisko_pipeline.sif` built from `Singularity`
- **Conda env for Nextflow + tools**: `environment.yml` (env name: `nf_env`)

### Downstream analysis tools (Python)

All Python scripts live in `src/` and are importable if you put `src/` on `PYTHONPATH`.

- `src/read_taxonomy.py`: merge GTDB-Tk taxonomy (`gtdbtk_summary.tsv`) with MAG abundance (`bin_summary.tsv`) and generate publication-quality stacked barplots (domain → genus; all samples + TOP/BOTTOM subsets; with/without “Unclassified”).
- `src/merge_all_results.py`: merge multiple `.tsv` files in a directory into one combined TSV.
- `src/compare_results.py`: generate text reports comparing taxonomic composition across locations and layers.
- `src/create_samplesheet.py`: generate nf-core sample sheets from a directory of trimmed paired-end reads.

## Repository layout

Common top-level directories:

- `abisko_results/`: example nf-core/mag outputs (assembly, binning, taxonomy, plots, MultiQC, etc.)
- `config/`: Nextflow configuration (e.g. `custom_default.config`)
- `databases/`: reference databases (e.g. GTDB-Tk data)
- `logs/`: pipeline logs and helper logs
- `report/`: LaTeX report sources
- `results/`: merged / post-processed outputs
- `samplesheet/`: generated sample sheets used as pipeline input
- `src/`: Python + shell utilities (post-processing, plotting, automation)
- `tests/`: pytest suite for the Python utilities

## Requirements

### For running the nf-core/mag pipeline

- Linux + adequate compute
- Conda/Mamba (recommended) OR an existing HPC module stack
- Nextflow and Java (provided by `environment.yml`)
- Singularity/Apptainer (runner script uses `-profile singularity`)

### For running the downstream Python analysis

- Python (see `pyproject.toml`; this project targets Python >= 3.12)

The Python tool dependencies are intentionally small (pandas/matplotlib/seaborn).

## Quickstart (Python tools)

Create a local virtual environment and install the project:

```bash
make venv
make install
```

Run the unit tests:

```bash
make install-dev
make test
```

Lint / auto-format:

```bash
make lint
make lint-fix
```

Tip: if you want to run scripts without installing, prefix with `PYTHONPATH=src`.

## Running the nf-core/mag pipeline

1) Create/update the pipeline environment:

```bash
make conda_env
conda activate nf_env
```

2) Run the pipeline (parameters are primarily controlled via `config/custom_default.config`):

```bash
bash src/nf_pipeline_default_config.sh
```

This writes a timestamped log to `logs/` and runs nf-core/mag with Singularity.

## Post-processing & analysis workflows

### 1) Generate nf-core sample sheets

`src/create_samplesheet.py` can generate grouped sample sheets based on a filename convention like:

`MEGAHIT-Sample_ID39-KF_5_TOP_AAA-TTT_L002_R1_001.fastq.gz`

Notes:

- The script contains default absolute paths for the author’s environment; you’ll typically want to pass your own directories.
- The most reliable way is to call the function directly:

```bash
PYTHONPATH=src python -c "from create_samplesheet import create_samplesheets; create_samplesheets(raw_data_dir='PATH/TO/Trimmed', output_dir='samplesheet')"
```

Outputs are written under `samplesheet/` (e.g. `samplesheet/kf_top/kf_top_samplesheet.csv`).

### 2) Create taxonomic abundance plots (GTDB-Tk + binning)

This merges:

- GTDB-Tk taxonomy: `.../Taxonomy/GTDB-Tk/gtdbtk_summary.tsv`
- Binning abundance matrix: `.../GenomeBinning/bin_summary.tsv` (expects columns starting with `Depth `)

Example:

```bash
python3 src/read_taxonomy.py \
  -i abisko_results/kj_results/Taxonomy/GTDB-Tk/gtdbtk_summary.tsv \
  -b abisko_results/kj_results/GenomeBinning/bin_summary.tsv \
  -o abisko_results/kj_results/plots/
```

The script generates multiple `.png` plots (domain/phylum/class/order/family/genus) including TOP-only and BOTTOM-only variants.

### 3) Merge per-sample TSVs into one table

If you have a directory containing many `.tsv` files (same columns), merge them into one:

```bash
python3 src/merge_all_results.py -i abisko_results/merged_results
```

By default this writes `all_samples_merged.tsv` into the input directory, or you can specify an output path:

```bash
python3 src/merge_all_results.py -i abisko_results/merged_results -o results/all_samples_merged.tsv
```

### 4) Generate comparative taxonomy reports

`src/compare_results.py` consumes a merged TSV with (at minimum) `user_genome` and `classification` columns.
It extracts `location` (SF/KF/KJ) and `layer` (TOP/BOTTOM) from `user_genome` names.

Example:

```bash
python3 src/compare_results.py results/all_samples_merged.tsv --output results/taxonomy_reports
```

It produces a `00_master_report.txt` plus several detailed report files in the output directory.

## Database download helpers

There is a helper script `src/download_gtdb-tk.sh` for downloading GTDB-Tk split packages.
It currently uses an absolute `DOWNLOAD_DIR`; update that variable before running.

You can run it via the Makefile (runs in a detached `screen` session):

```bash
make download_gtdb-tk
tail -f logs/gtdbtk_download.log
```

## Reproducibility with Singularity/Apptainer

To (re)build the container image from the `Singularity` definition:

```bash
make build-image
```

## Contact

For questions or contributions, contact Chandrashekar CR at ch1131ch-s@student.lu.se.
