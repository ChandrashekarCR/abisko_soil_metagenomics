import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib

matplotlib.use("Agg", force=True)

import pytest


@pytest.fixture
def gtdbtk_tsv(tmp_path):
    path = tmp_path / "gtdbtk_summary.tsv"
    path.write_text(
        "user_genome\tclassification\n"
        "bin_1\td__Bacteria;p__Proteobacteria;c__Gammaproteobacteria;o__Enterobacterales;f__Enterobacteriaceae;g__Escherichia;s__coli\n"
        "bin_2\td__Archaea;p__Euryarchaeota;c__Methanobacteria;o__Methanobacteriales;f__Methanobacteriaceae;g__Methanobacterium;s__\n"
        "bin_missing\t\n"
    )
    return path


@pytest.fixture
def bins_tsv(tmp_path):
    path = tmp_path / "bin_summary.tsv"
    path.write_text("bin\tDepth 1 TOP\tDepth 2 BOTTOM\nbin_1\t1\t3\nbin_2\t3\t1\n")
    return path


@pytest.fixture
def sample_reads_dir(tmp_path):
    raw_dir = tmp_path / "Trimmed"
    raw_dir.mkdir()

    filenames = [
        "MEGAHIT-Sample_ID39-KF_5_TOP_AAA-TTT_L002_R1_001.fastq.gz",
        "MEGAHIT-Sample_ID39-KF_5_TOP_AAA-TTT_L002_R2_001.fastq.gz",
        "MEGAHIT-Sample_ID41-KF_7_TOP_CCC-GGG_L002_R1_001.fastq.gz",
        "MEGAHIT-Sample_ID41-KF_7_TOP_CCC-GGG_L002_R2_001.fastq.gz",
        "ignored.txt",
    ]

    for name in filenames:
        (raw_dir / name).write_text("test")

    return raw_dir
