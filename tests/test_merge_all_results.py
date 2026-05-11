import pandas as pd
import pytest

from merge_all_results import merge_all_tsv_files


@pytest.fixture
def sample_tsv_files(tmp_path):
    """Create sample TSV files for merging."""
    # Create first TSV file
    df1 = pd.DataFrame(
        {
            "user_genome": ["bin_1", "bin_2"],
            "classification": [
                "d__Bacteria;p__Proteobacteria",
                "d__Archaea;p__Euryarchaeota",
            ],
        }
    )
    file1 = tmp_path / "sample_1.tsv"
    df1.to_csv(file1, sep="\t", index=False)

    # Create second TSV file
    df2 = pd.DataFrame(
        {
            "user_genome": ["bin_3", "bin_4"],
            "classification": [
                "d__Bacteria;p__Firmicutes",
                "d__Bacteria;p__Proteobacteria",
            ],
        }
    )
    file2 = tmp_path / "sample_2.tsv"
    df2.to_csv(file2, sep="\t", index=False)

    # Create third TSV file
    df3 = pd.DataFrame(
        {
            "user_genome": ["bin_5"],
            "classification": ["d__Archaea;p__Euryarchaeota"],
        }
    )
    file3 = tmp_path / "sample_3.tsv"
    df3.to_csv(file3, sep="\t", index=False)

    return tmp_path


def test_merge_all_tsv_files_default_output(sample_tsv_files):
    """Test merging TSV files with default output filename."""
    output_file = sample_tsv_files / "all_samples_merged.tsv"

    merge_all_tsv_files(str(sample_tsv_files))

    assert output_file.exists()


def test_merge_all_tsv_files_custom_output(sample_tsv_files):
    """Test merging TSV files with custom output filename."""
    output_file = sample_tsv_files / "custom_merged.tsv"

    merge_all_tsv_files(str(sample_tsv_files), str(output_file))

    assert output_file.exists()


def test_merge_all_tsv_files_combines_data(sample_tsv_files):
    """Test that merged file contains all data from input files."""
    output_file = sample_tsv_files / "all_samples_merged.tsv"

    merge_all_tsv_files(str(sample_tsv_files), str(output_file))

    # Read the merged file
    merged_df = pd.read_csv(output_file, sep="\t")

    # Check that all rows are present (3 files with 2, 2, and 1 rows respectively)
    assert len(merged_df) == 5
    assert "user_genome" in merged_df.columns
    assert "classification" in merged_df.columns


def test_merge_all_tsv_files_preserves_columns(sample_tsv_files):
    """Test that merged file preserves column order and names."""
    output_file = sample_tsv_files / "all_samples_merged.tsv"

    merge_all_tsv_files(str(sample_tsv_files), str(output_file))

    merged_df = pd.read_csv(output_file, sep="\t")

    expected_columns = ["user_genome", "classification"]
    assert list(merged_df.columns) == expected_columns


def test_merge_all_tsv_files_data_integrity(sample_tsv_files):
    """Test that data values are preserved during merge."""
    output_file = sample_tsv_files / "all_samples_merged.tsv"

    merge_all_tsv_files(str(sample_tsv_files), str(output_file))

    merged_df = pd.read_csv(output_file, sep="\t")

    # Check that specific values are in the merged file
    assert "bin_1" in merged_df["user_genome"].values
    assert "bin_3" in merged_df["user_genome"].values
    assert "bin_5" in merged_df["user_genome"].values
    assert "d__Bacteria;p__Proteobacteria" in merged_df["classification"].values


def test_merge_empty_directory(tmp_path):
    """Test behavior when directory has no TSV files."""
    output_file = tmp_path / "empty_merged.tsv"

    # This should not crash; the function should print a message
    merge_all_tsv_files(str(tmp_path), str(output_file))

    # Output file should not be created
    assert not output_file.exists()


def test_merge_single_file(tmp_path):
    """Test merging when only one TSV file is present."""
    # Create a single TSV file
    df = pd.DataFrame(
        {
            "user_genome": ["bin_1", "bin_2"],
            "classification": [
                "d__Bacteria;p__Proteobacteria",
                "d__Archaea;p__Euryarchaeota",
            ],
        }
    )
    tsv_file = tmp_path / "single_sample.tsv"
    df.to_csv(tsv_file, sep="\t", index=False)

    output_file = tmp_path / "merged.tsv"
    merge_all_tsv_files(str(tmp_path), str(output_file))

    merged_df = pd.read_csv(output_file, sep="\t")

    # Should have all rows from the single file
    assert len(merged_df) == 2
    assert list(merged_df.columns) == ["user_genome", "classification"]
