Bootstrap: docker
From: mambaorg/micromamba:1.5.10

%labels
    Author Chandrashekar CR
    Version 1.0
    Description "Bioinformatics pipeline for nextflow analysis on the Abisko metagenome."

%help
    This container includes a bioinformatics pipeline that uses the nf-core/mag workflow.
    This container includes all the environment and the tools required to carryout reproducible analysis.
    - Nextflow
    - Kraken2
    - bracken
    - Python 3.13
    ..

    Usage:
        apptainer shell container.sif
        apptainer exce container.sif nextflow --version
        apptainer run container.sif


%files
    # Copy the files into the container which are required
    