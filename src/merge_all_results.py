import os
import pandas as pd
import argparse
from pathlib import Path


def merge_all_tsv_files(input_dir, output_file=None):
    """
    Merge all TSV files in a directory into a single file.

    :param input_dir: Directory containing TSV files to merge
    :param output_file: Output file path (default: all_samples_merged.tsv)
    """
    if output_file is None:
        output_file = os.path.join(input_dir, "all_samples_merged.tsv")

    # Find all TSV files in the directory
    tsv_files = sorted(Path(input_dir).glob("*.tsv"))

    if not tsv_files:
        print(f"No TSV files found in {input_dir}")
        return

    print(f"Found {len(tsv_files)} TSV file(s) to merge:")
    for file in tsv_files:
        print(f"  - {file.name}")

    # Read and merge all TSV files
    dataframes = []
    for tsv_file in tsv_files:
        print(f"\nReading {tsv_file.name}...")
        try:
            df = pd.read_csv(tsv_file, sep="\t")
            print(f"  Rows: {len(df)}")
            dataframes.append(df)
        except Exception as e:
            print(f"  ERROR reading {tsv_file.name}: {str(e)}")

    if not dataframes:
        print("No valid TSV files to merge.")
        return

    # Concatenate all dataframes
    print("\nMerging dataframes...")
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Save merged result
    merged_df.to_csv(output_file, sep="\t", index=False)
    print(f"\nSaved merged result: {output_file}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print("MERGED RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total files merged: {len(tsv_files)}")
    print(f"Total rows: {len(merged_df)}")
    print(f"Total columns: {len(merged_df.columns)}")
    print(f"\nColumns: {', '.join(merged_df.columns.tolist())}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="merge_all_results.py",
        description="Merge all TSV files in a directory into a single TSV file",
        usage="python3 merge_all_results.py -i <input_dir> -o <output_file>",
    )
    parser.add_argument(
        "-i",
        "--input_dir",
        dest="input_dir",
        required=True,
        help="Directory containing TSV files to merge",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        dest="output_file",
        default=None,
        help="Output TSV file path (default: all_samples_merged.tsv in input directory)",
    )

    args = parser.parse_args()

    merge_all_tsv_files(args.input_dir, args.output_file)


"""
Example usage:
python3 src/merge_all_results.py -i merged_results
python3 src/merge_all_results.py -i merged_results -o merged_results/complete_dataset.tsv
"""
