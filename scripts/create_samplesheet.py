import os
import re
import csv
from collections import defaultdict

RAW_DATA_DIR = "/home2/projects/dag/Abisko/0_rawdata/Trimmed"
OUTPUT_DIR = "/home/inf-21-2024/nbis/samplesheet"

samples = defaultdict(list)

# Find all R1 and R2 files
for file in sorted(os.listdir(RAW_DATA_DIR)):
    if file.endswith(".fastq.gz"):
        # Extract the sample and group info
        match_string = re.search(r'(ID\d+)-(KJ|KF|SF)_(\d+)_(TOP|BOTTOM)_[ATGC]+-[ATGC]+_L002_R(1|2)_001.fastq.gz', file)
        if match_string:
            folder_name = f"Sample_{match_string.group(1)}-{match_string.group(2)}_{match_string.group(3)}_{match_string.group(4)}"
            samples[folder_name].append(os.path.join(RAW_DATA_DIR,file))


# Define the 6 subdirectories and their filters
categories = [
    ("kj_top", "KJ", "TOP"),
    ("kj_bottom", "KJ", "BOTTOM"),
    ("kf_top", "KF", "TOP"),
    ("kf_bottom", "KF", "BOTTOM"),
    ("sf_top", "SF", "TOP"),
    ("sf_bottom", "SF", "BOTTOM"),
]

# Create sample sheets for each category
for dir_name, group, position in categories:
    dir_path = os.path.join(OUTPUT_DIR, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    
    csv_path = os.path.join(dir_path, f"{dir_name}_samplesheet.csv")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["sample", "group", "short_reads_1", "short_reads_2", "long_reads", "short_reads_platform"])
        
        # Write sample rows
        for sample_name, file_paths in sorted(samples.items()):
            if group in sample_name and position in sample_name:
                # Separate R1 and R2 files
                r1_file = next((fp for fp in file_paths if "_R1_" in fp), "")
                r2_file = next((fp for fp in file_paths if "_R2_" in fp), "")
                
                group_label = f"{group}_{position}"
                writer.writerow([sample_name, group_label, r1_file, r2_file, "", "ILLUMINA"])
    
    print(f"Created {csv_path}")