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
        apptainer exec container.sif nextflow --version
        apptainer run container.sif


%files
    # Copy the files into the container which are required
    environment.yml /opt/environment.yml
    config/custom_default.config /opt/config/custom_default.config
    scripts /opt/scripts
    samplesheet/kj_samplesheet.csv /opt/samplesheet/kj_samplesheet.csv

%environment
    # Add conda to the PATH variable
    export PATH="/opt/envs/nf_env/bin:$PATH" 
    export CONDA_PREFIX="/opt/envs/nf_env"
    export LC_ALL=C
    

# This section runs during the container build time
%post
    # Update the system packages and install the basic utilities like wget, curl, git build-esstial etc.
    apt-get update && apt-get install -y \
        wget \
        curl \
        git \
        build-essential \
        ca-certificates \
        procps \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    # Then we need to set the environment variables for miniconda
    export MAMBA_ROOT_PREFIX=/opt/conda
    export PATH="/opt/conda/bin:$PATH"

    # Create conda environment from the environment.yml file 
    # -y yes to all prompts
    # -f file path to the environment.yml file
    # -p prefix where to install the environment
    /bin/micromamba create -y -f /opt/environment.yml -p /opt/envs/nf_env

    # Clean up conda/mamba cache to reduce image size
    /bin/micromamba clean -a -y 

    # Make the scripts excecutable
    chmod +x /opt/scripts/*

    echo "Container build complete!"

%runscript
    # This is excecuted when the "apptainer run container.sif"
    printf '%.0s=' {1..40}
    echo "Abisko Metagenome Analysis Container"
    printf '%.0s=' {1..40}
    echo "Available tools:"
    echo " - Nextflow"
    echo " - Kraken2"
    echo " - Bracken"
    echo " - Python 3.13 with other libraries"
    printf '%.0s=' {1..40}
    echo "Usage examples:"
    echo " apptainer exec container.sif nextflow --version"
    echo " apptainer exec container.sif kraken2 --version"
    echo " apptainer shell container.sif"
    echo "Opening interactive shell..."
    exec /bin/bash "$@"

%test
    # Test run after successful build to verify the container works
    echo "Running container tests..."

    # Set PATH for testing
    export PATH="/opt/envs/nf_env/bin:$PATH"

    # Test that key tools are availlable
    echo "Checking for Python..."
    which python3 || exit 1

    echo "Checking for Nextflow..."
    which nextflow || exit 1

    echo "Checking for Kraken2..."
    which kraken2 || exit 1

    echo "Checking for Bracken.."
    which bracken || exit 1

    # Test tool versions
    echo ""
    echo "Tool versions:"
    python3 --version
    nextflow -version
    kraken2 --version
    
    echo ""
    echo "All tests passed!"