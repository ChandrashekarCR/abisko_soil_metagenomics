import csv

from create_samplesheet import collect_samples, create_samplesheets, extract_sample_name


def test_extract_sample_name_parses_expected_filename():
    filename = "MEGAHIT-Sample_ID39-KF_5_TOP_AAA-TTT_L002_R1_001.fastq.gz"
    assert extract_sample_name(filename) == "Sample_ID39-KF_5_TOP"


def test_collect_samples_groups_r1_and_r2(sample_reads_dir):
    samples = collect_samples(str(sample_reads_dir))

    assert sorted(samples.keys()) == ["Sample_ID39-KF_5_TOP", "Sample_ID41-KF_7_TOP"]
    assert len(samples["Sample_ID39-KF_5_TOP"]) == 2
    assert any("_R1_" in path for path in samples["Sample_ID39-KF_5_TOP"])
    assert any("_R2_" in path for path in samples["Sample_ID39-KF_5_TOP"])


def test_create_samplesheets_writes_expected_csv(sample_reads_dir, tmp_path):
    output_dir = tmp_path / "samplesheet"
    create_samplesheets(raw_data_dir=str(sample_reads_dir), output_dir=str(output_dir))

    csv_path = output_dir / "kf_top" / "kf_top_samplesheet.csv"
    assert csv_path.exists()

    with open(csv_path, newline="") as f:
        rows = list(csv.reader(f))

    assert rows[0] == [
        "sample",
        "group",
        "short_reads_1",
        "short_reads_2",
        "long_reads",
        "short_reads_platform",
    ]
    assert rows[1][0] == "Sample_ID39-KF_5_TOP"
    assert rows[1][1] == "KF_TOP"
    assert rows[1][5] == "ILLUMINA"
    assert rows[2][0] == "Sample_ID41-KF_7_TOP"
