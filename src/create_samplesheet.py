import os
import re
import csv
from collections import defaultdict

RAW_DATA_DIR = "/home2/projects/dag/Abisko/0_rawdata/Trimmed"
OUTPUT_DIR = "/home/inf-21-2024/nbis/samplesheet"

SAMPLE_REGEX = re.compile(
    r"(ID\d+)-(KJ|KF|SF)_(\d+)_(TOP|BOTTOM)_[ATGC]+-[ATGC]+_L002_R(1|2)_001.fastq.gz"
)

CATEGORIES = [
    ("kj_top", "KJ", "TOP"),
    ("kj_bottom", "KJ", "BOTTOM"),
    ("kf_top", "KF", "TOP"),
    ("kf_bottom", "KF", "BOTTOM"),
    ("sf_top", "SF", "TOP"),
    ("sf_bottom", "SF", "BOTTOM"),
]


def extract_sample_name(filename):
    match = SAMPLE_REGEX.search(filename)
    if not match:
        return None
    return f"Sample_{match.group(1)}-{match.group(2)}_{match.group(3)}_{match.group(4)}"


def collect_samples(raw_data_dir):
    samples = defaultdict(list)

    for file in sorted(os.listdir(raw_data_dir)):
        if file.endswith(".fastq.gz"):
            sample_name = extract_sample_name(file)
            if sample_name:
                samples[sample_name].append(os.path.join(raw_data_dir, file))

    return samples


def write_samplesheet(csv_path, samples, group, position):
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "sample",
                "group",
                "short_reads_1",
                "short_reads_2",
                "long_reads",
                "short_reads_platform",
            ]
        )

        for sample_name, file_paths in sorted(samples.items()):
            if group in sample_name and position in sample_name:
                r1_file = next((fp for fp in file_paths if "_R1_" in fp), "")
                r2_file = next((fp for fp in file_paths if "_R2_" in fp), "")
                group_label = f"{group}_{position}"
                writer.writerow(
                    [sample_name, group_label, r1_file, r2_file, "", "ILLUMINA"]
                )


def create_samplesheets(raw_data_dir=RAW_DATA_DIR, output_dir=OUTPUT_DIR):
    samples = collect_samples(raw_data_dir)

    for dir_name, group, position in CATEGORIES:
        dir_path = os.path.join(output_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        csv_path = os.path.join(dir_path, f"{dir_name}_samplesheet.csv")
        write_samplesheet(csv_path, samples, group, position)
        print(f"Created {csv_path}")


def main():
    create_samplesheets()


if __name__ == "__main__":
    main()
