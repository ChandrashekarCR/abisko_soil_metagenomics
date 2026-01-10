Bootstrap: docker
From: mambaorg/micromamba:1.5.10

%labels
    Author Chandrashekar CR
    Version 1.0
    Description Bioinformatics pipeline container with Nextflow, Kraken2, BLAST, and other tools

%help
    This container includes a bioinformatics environment with:
    - Nextflow (workflow management)
    - Kraken2 (taxonomic classification)
    - BLAST (sequence alignment)
    - Bracken (abundance estimation)
    - Python 3.13
    - Various bioinformatics utilities
    
    Usage:
        apptainer shell container.sif
        apptainer exec container.sif nextflow --version
        apptainer run container.sif

%files
    # Copy the conda environment file into the container
    environment.yml /opt/environment.yml

%environment
    # Set environment variables that will be available at runtime
    export PATH="/opt/conda/bin:$PATH"
    export CONDA_PREFIX="/opt/conda"
    export LC_ALL=C

%post
    # This section runs during container build time
    
    # Update system packages and install basic utilities
    apt-get update && apt-get install -y \
        wget \
        curl \
        git \
        build-essential \
        ca-certificates \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Initialize micromamba
    export MAMBA_ROOT_PREFIX=/opt/conda
    export PATH="/opt/conda/bin:$PATH"
    
    # Create conda environment from the environment.yml file
    /bin/micromamba create -y -f /opt/environment.yml -p /opt/conda
    
    # Clean up conda/mamba cache to reduce image size
    /bin/micromamba clean -a -y
    
    echo "Container build complete!"

%runscript
    # This is executed when you run: apptainer run container.sif
    echo "Bioinformatics Container - Nextflow Pipeline Environment"
    echo "Available tools: nextflow, kraken2, blast, bracken, python"
    echo ""
    echo "Usage examples:"
    echo "  apptainer exec container.sif nextflow --version"
    echo "  apptainer exec container.sif kraken2 --version"
    echo "  apptainer shell container.sif"
    exec /bin/bash "$@"

%test
    # Tests run after successful build to verify the container works
    echo "Testing container..."
    export PATH="/opt/conda/bin:$PATH"
    
    # Test that key tools are available
    which python || exit 1
    which nextflow || exit 1
    which kraken2 || exit 1
    which blastn || exit 1
    
    # Test tool versions
    python --version
    nextflow -version
    kraken2 --version
    
    echo "All tests passed!"
