import pandas as pd
import pytest
from pathlib import Path

from compare_results import TaxonomyAnalyzer


@pytest.fixture
def sample_taxonomy_tsv(tmp_path):
    """Create a sample taxonomy TSV file for testing."""
    data = {
        "user_genome": [
            "MEGAHIT-bin_1-sample1-KF_5_TOP_AAA.fastq.gz",
            "MEGAHIT-bin_2-sample2-KF_5_BOTTOM_AAA.fastq.gz",
            "MEGAHIT-bin_3-sample3-SF_10_TOP_CCC.fastq.gz",
            "MEGAHIT-bin_4-sample4-SF_10_BOTTOM_CCC.fastq.gz",
            "MEGAHIT-bin_5-sample5-KJ_3_TOP_TTT.fastq.gz",
        ],
        "classification": [
            "d__Bacteria;p__Proteobacteria;c__Gammaproteobacteria;o__Enterobacterales;f__Enterobacteriaceae;g__Escherichia;s__coli",
            "d__Bacteria;p__Firmicutes;c__Bacilli;o__Bacillales;f__Bacillaceae;g__Bacillus;s__subtilis",
            "d__Bacteria;p__Proteobacteria;c__Gammaproteobacteria;o__Enterobacterales;f__Enterobacteriaceae;g__Escherichia;s__coli",
            "d__Archaea;p__Euryarchaeota;c__Methanobacteria;o__Methanobacteriales;f__Methanobacteriaceae;g__Methanobacterium;s__",
            "d__Bacteria;p__Firmicutes;c__Bacilli;o__Bacillales;f__Bacillaceae;g__Bacillus;s__subtilis",
        ],
    }

    tsv_file = tmp_path / "test_taxonomy.tsv"
    df = pd.DataFrame(data)
    df.to_csv(tsv_file, sep="\t", index=False)

    return tsv_file


def test_taxonomy_analyzer_initialization(sample_taxonomy_tsv, tmp_path):
    """Test that TaxonomyAnalyzer initializes correctly."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    assert analyzer.df is not None
    assert len(analyzer.df) == 5
    assert "location" in analyzer.df.columns
    assert "layer" in analyzer.df.columns


def test_taxonomy_analyzer_extracts_metadata(sample_taxonomy_tsv, tmp_path):
    """Test that metadata is correctly extracted from genome names."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    assert "KF" in analyzer.df["location"].values
    assert "SF" in analyzer.df["location"].values
    assert "KJ" in analyzer.df["location"].values
    assert "TOP" in analyzer.df["layer"].values
    assert "BOTTOM" in analyzer.df["layer"].values


def test_taxonomy_analyzer_cleans_taxonomy(sample_taxonomy_tsv, tmp_path):
    """Test that taxonomy prefixes are removed."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    # Check that prefixes are removed
    assert "Bacteria" in analyzer.df["domain"].values
    assert "d__Bacteria" not in analyzer.df["domain"].values
    assert "Proteobacteria" in analyzer.df["phylum"].values
    assert "p__Proteobacteria" not in analyzer.df["phylum"].values


def test_analyze_layer_distribution_generates_report(sample_taxonomy_tsv, tmp_path):
    """Test that layer distribution analysis generates a report."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    report = analyzer.analyze_layer_distribution()

    assert "LAYER DISTRIBUTION ANALYSIS" in report
    assert "TOP" in report
    assert "BOTTOM" in report
    assert len(report) > 0

    report_file = Path(output_dir) / "01_layer_distribution_analysis.txt"
    assert report_file.exists()


def test_analyze_cross_location_comparison(sample_taxonomy_tsv, tmp_path):
    """Test that cross-location comparison generates a report."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    report = analyzer.analyze_cross_location_comparison()

    assert "CROSS-LOCATION COMPARISON" in report
    assert len(report) > 0

    report_file = Path(output_dir) / "04_cross_location_comparison.txt"
    assert report_file.exists()


def test_generate_comprehensive_report(sample_taxonomy_tsv, tmp_path):
    """Test that all reports are generated."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    reports = analyzer.generate_comprehensive_report()

    assert len(reports) == 5
    assert "Layer Distribution" in reports
    assert "Cross-Layer Summary" in reports
    assert "Location Distribution" in reports
    assert "Cross-Location Comparison" in reports
    assert "Abundance Summary" in reports


def test_generate_master_report(sample_taxonomy_tsv, tmp_path):
    """Test that master report is generated."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    master_report = analyzer.generate_master_report()

    assert "COMPREHENSIVE TAXONOMIC ANALYSIS" in master_report
    assert "MASTER REPORT" in master_report
    assert str(len(analyzer.df)) in master_report

    report_file = Path(output_dir) / "00_master_report.txt"
    assert report_file.exists()


def test_all_report_files_created(sample_taxonomy_tsv, tmp_path):
    """Test that all expected report files are created."""
    output_dir = tmp_path / "reports"
    analyzer = TaxonomyAnalyzer(str(sample_taxonomy_tsv), output_dir=str(output_dir))

    analyzer.generate_master_report()
    analyzer.generate_comprehensive_report()

    expected_files = [
        "00_master_report.txt",
        "01_layer_distribution_analysis.txt",
        "02_cross_layer_summary.txt",
        "03_location_distribution.txt",
        "04_cross_location_comparison.txt",
        "05_abundance_summary.txt",
    ]

    output_path = Path(output_dir)
    for file in expected_files:
        assert (output_path / file).exists(), f"Expected file {file} not found"
