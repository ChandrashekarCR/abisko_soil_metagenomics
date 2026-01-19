# Abisko Soil Metagenomics Project

This project analyzes soil metagenomic data from the Abisko region using the nf-core/mag pipeline and custom scripts for downstream analysis and visualization.

## Project Structure

- **abisko_results/**: Contains results from the nf-core/mag pipeline, including annotation, assembly, genome binning, quality control, taxonomy, and plots for different samples.
- **config/**: Custom Nextflow configuration files for pipeline optimization to run on server (e.g., `custom_default.config`).
- **databases/**: Reference databases for taxonomic classification (e.g., GTDB-Tk).
- **failed_results/**: Stores results from failed pipeline runs and temporary outputs for debugging and for better resource allocations.
- **logs/**: Log files from pipeline executions.
- **notebooks/**: Jupyter notebooks for exploratory data analysis.
- **results/**: Output directory for processed data, including annotation, assembly, pipeline reports, and QC results.
- **samplesheet/**: Sample sheet CSV files describing input samples for the pipeline.
- **scripts/**: Custom scripts for data processing and visualization, such as:
  - `read_taxonomy.py`: Reads GTDB-Tk taxonomy outputs and binning results, merges them, and generates publication-quality taxonomic abundance plots.
  - `create_samplesheet.py`: Script to generate sample sheets.
  - `download_gtdb-tk.sh`: Scripts for database setup and pipeline configuration.
- **work/**: Nextflow working directory for intermediate files.
- **environment.yml** / **requirements.txt**: Environment and dependency specifications for reproducibility.
- **Makefile**: Automation of common tasks.
- **Singularity**: Container definition for reproducible pipeline execution.

## Main Workflow

1. **Sample Sheet Preparation**: Define samples in `samplesheet/`.
2. **Pipeline Execution**: Run the nf-core/mag pipeline with custom configuration for assembly, binning, annotation, and taxonomic classification.
3. **Post-processing & Visualization**: Use scripts in `scripts/` (notably `read_taxonomy.py`) to merge taxonomy and abundance data, and generate plots for publication.

## Requirements
- Linux system with sufficient resources (recommended: 250 CPUs, 2TB RAM)
- [Nextflow](https://www.nextflow.io/) and [nf-core/mag](https://nf-co.re/mag)
- Conda or Singularity for environment and container management
- Python 3 with packages listed in `requirements.txt` or `environment.yml`

## Example Usage

To run the pipeline:
```bash
screen -S kj_samples
conda activate nf_env
bash scripts/nf_pipeline_default_config.sh

```
To generate taxonomic abundance plots after running the pipeline:
```bash
python3 scripts/read_taxonomy.py \
  -i abisko_results/kj_results/Taxonomy/GTDB-Tk/gtdbtk_summary.tsv \
  -b abisko_results/kj_results/GenomeBinning/bin_summary.tsv \
  -o abisko_results/kj_results/plots/
```

## Contact
For questions or contributions, please contact Chandrashekar CR [ch1131ch-s@student.lu.se](ch1131ch-s@student.lu.se).
