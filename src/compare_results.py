import pandas as pd
import os
import numpy as np
from datetime import datetime
from pathlib import Path
import argparse


class TaxonomyAnalyzer:
    """
    Comprehensive taxonomic analysis tool for metagenomic binning data.
    Analyzes distribution of organisms across locations and layers.
    Generates detailed reports organized by analysis type.
    """
    
    def __init__(self, tsv_file, output_dir="taxonomy_reports"):
        """
        Initialize the TaxonomyAnalyzer.
        
        :param tsv_file: Path to the merged taxonomy TSV file
        :param output_dir: Directory to save report files
        """
        self.tsv_file = tsv_file
        self.output_dir = output_dir
        self.df = None
        self.locations = ["SF", "KF", "KJ"]
        self.tax_levels = ["phylum", "class", "order", "family", "genus", "species"]
        self.prefixes = {
            "domain": "d__", "phylum": "p__", "class": "c__", "order": "o__",
            "family": "f__", "genus": "g__", "species": "s__"
        }
        
        # Create output directory
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Load and process data
        self._load_and_process_data()
    
    def _load_and_process_data(self):
        """Load and preprocess the taxonomy data."""
        print("Loading data from:", self.tsv_file)
        
        # Read CSV
        self.df = pd.read_csv(self.tsv_file, sep='\t').iloc[:, :2]
        self.df = self.df.dropna(axis=0)
        
        # Extract metadata from user_genome column
        self.df['bin'] = self.df['user_genome'].apply(lambda x: x.split("-")[1])
        self.df['location'] = self.df['user_genome'].apply(
            lambda x: x.split("-")[3].split(".")[0].split("_")[0]
        )
        self.df['layer'] = self.df['user_genome'].apply(
            lambda x: x.split("-")[3].split(".")[0].split("_")[2]
        )
        
        # Parse taxonomy columns
        self.df["domain"] = self.df['classification'].apply(lambda x: self._safe_split(x, 0))
        self.df["phylum"] = self.df['classification'].apply(lambda x: self._safe_split(x, 1))
        self.df["class"] = self.df['classification'].apply(lambda x: self._safe_split(x, 2))
        self.df["order"] = self.df['classification'].apply(lambda x: self._safe_split(x, 3))
        self.df["family"] = self.df['classification'].apply(lambda x: self._safe_split(x, 4))
        self.df["genus"] = self.df['classification'].apply(lambda x: self._safe_split(x, 5))
        self.df["species"] = self.df['classification'].apply(lambda x: self._safe_split(x, 6))
        
        # Clean up taxonomy columns
        self._clean_taxonomy_columns()
        
        print(f"Data loaded successfully. Total bins: {len(self.df)}")
        print(f"Locations: {', '.join(self.df['location'].unique())}")
        print(f"Layers: {', '.join(self.df['layer'].unique())}\n")
    
    @staticmethod
    def _safe_split(value, index, delimiter=";"):
        """Safely split and extract taxonomy level."""
        try:
            parts = str(value).split(delimiter)
            return parts[index] if index < len(parts) else "Unclassified"
        except:
            return "Unclassified"
    
    def _clean_taxonomy_columns(self):
        """Remove prefixes and standardize taxonomy columns."""
        taxonomy_cols = ["domain", "phylum", "class", "order", "family", "genus", "species"]
        
        for col in taxonomy_cols:
            # Remove prefix
            self.df[col] = self.df[col].apply(
                lambda x: x.replace(self.prefixes[col], "") if isinstance(x, str) else x
            )
            # Replace empty strings with "None"
            self.df[col] = self.df[col].apply(
                lambda x: "None" if (isinstance(x, str) and x.strip() == "") else x
            )
    
    def _write_report(self, filename, content):
        """Write report content to a file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Report saved: {filepath}")
        return filepath
    
    def _format_header(self, title, level=1):
        """Format section header."""
        if level == 1:
            return f"\n{'='*80}\n{title}\n{'='*80}\n"
        else:
            return f"\n{'-'*80}\n{title}\n{'-'*80}\n"
    
    def analyze_layer_distribution(self):
        """
        Analyze taxonomic distribution across layers (TOP and BOTTOM) for each location.
        Generates detailed reports for each location.
        """
        report = self._format_header("PART 1: LAYER DISTRIBUTION ANALYSIS")
        report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "Analysis of organisms at TOP and BOTTOM layers for each location.\n"
        report += f"Taxonomic levels analyzed: {', '.join(self.tax_levels)}\n"
        
        for loc in self.locations:
            report += self._format_header(f"LOCATION: {loc}", level=1)
            
            loc_data = self.df[self.df['location'] == loc]
            top_data = loc_data[loc_data['layer'] == "TOP"]
            bottom_data = loc_data[loc_data['layer'] == "BOTTOM"]
            
            report += f"\nTotal bins in {loc}: {len(loc_data)}\n"
            report += f"  - TOP layer: {len(top_data)} bins\n"
            report += f"  - BOTTOM layer: {len(bottom_data)} bins\n"
            
            for tax_level in self.tax_levels:
                report += self._format_header(f"Taxonomic Level: {tax_level.upper()}", level=2)
                
                top_organisms = set(top_data[tax_level].unique()) - {"Unclassified", "None"}
                bottom_organisms = set(bottom_data[tax_level].unique()) - {"Unclassified", "None"}
                
                top_only = top_organisms - bottom_organisms
                bottom_only = bottom_organisms - top_organisms
                common = top_organisms & bottom_organisms
                
                report += f"\nTOP layer organisms ({len(top_organisms)} total):\n"
                for org in sorted(top_organisms):
                    count = len(top_data[top_data[tax_level] == org])
                    report += f"  • {org} ({count} bins)\n"
                
                report += f"\nBOTTOM layer organisms ({len(bottom_organisms)} total):\n"
                for org in sorted(bottom_organisms):
                    count = len(bottom_data[bottom_data[tax_level] == org])
                    report += f"  • {org} ({count} bins)\n"
                
                report += f"\n✓ COMMON (in both TOP and BOTTOM): {len(common)}\n"
                for org in sorted(common):
                    top_count = len(top_data[top_data[tax_level] == org])
                    bottom_count = len(bottom_data[bottom_data[tax_level] == org])
                    report += f"  • {org} (TOP: {top_count}, BOTTOM: {bottom_count})\n"
                
                report += f"\n✗ ONLY IN TOP (not in BOTTOM): {len(top_only)}\n"
                for org in sorted(top_only):
                    count = len(top_data[top_data[tax_level] == org])
                    report += f"  • {org} ({count} bins)\n"
                
                report += f"\n✗ ONLY IN BOTTOM (not in TOP): {len(bottom_only)}\n"
                for org in sorted(bottom_only):
                    count = len(bottom_data[bottom_data[tax_level] == org])
                    report += f"  • {org} ({count} bins)\n"
        
        self._write_report("01_layer_distribution_analysis.txt", report)
        return report
    
    def analyze_cross_layer_summary(self):
        """
        Analyze organisms that are common or unique across all TOP and BOTTOM layers globally.
        """
        report = self._format_header("PART 2: CROSS-LAYER SUMMARY - GLOBAL LAYER ANALYSIS")
        report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "Analysis of organisms common or unique to TOP/BOTTOM layers across all locations.\n"
        
        for tax_level in self.tax_levels:
            report += self._format_header(f"TAXONOMIC LEVEL: {tax_level.upper()}", level=1)
            
            all_top_organisms = set(self.df[self.df['layer'] == "TOP"][tax_level].unique()) - {"Unclassified", "None"}
            all_bottom_organisms = set(self.df[self.df['layer'] == "BOTTOM"][tax_level].unique()) - {"Unclassified", "None"}
            
            common_all_layers = all_top_organisms & all_bottom_organisms
            top_only_all = all_top_organisms - all_bottom_organisms
            bottom_only_all = all_bottom_organisms - all_top_organisms
            
            report += f"\nOrganisms COMMON across ALL TOP and ALL BOTTOM layers globally: {len(common_all_layers)}\n"
            for org in sorted(common_all_layers):
                top_count = len(self.df[(self.df['layer'] == "TOP") & (self.df[tax_level] == org)])
                bottom_count = len(self.df[(self.df['layer'] == "BOTTOM") & (self.df[tax_level] == org)])
                report += f"  • {org} (TOP: {top_count}, BOTTOM: {bottom_count})\n"
            
            report += f"\nOrganisms ONLY in TOP layers globally: {len(top_only_all)}\n"
            for org in sorted(top_only_all):
                count = len(self.df[(self.df['layer'] == "TOP") & (self.df[tax_level] == org)])
                locations_present = self.df[(self.df['layer'] == "TOP") & (self.df[tax_level] == org)]['location'].unique()
                report += f"  • {org} ({count} bins, locations: {', '.join(sorted(locations_present))})\n"
            
            report += f"\nOrganisms ONLY in BOTTOM layers globally: {len(bottom_only_all)}\n"
            for org in sorted(bottom_only_all):
                count = len(self.df[(self.df['layer'] == "BOTTOM") & (self.df[tax_level] == org)])
                locations_present = self.df[(self.df['layer'] == "BOTTOM") & (self.df[tax_level] == org)]['location'].unique()
                report += f"  • {org} ({count} bins, locations: {', '.join(sorted(locations_present))})\n"
        
        self._write_report("02_cross_layer_summary.txt", report)
        return report
    
    def analyze_location_distribution(self):
        """
        Analyze all organisms present in each location across all layers.
        """
        report = self._format_header("PART 3: LOCATION DISTRIBUTION ANALYSIS")
        report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "Complete taxonomic composition for each location.\n"
        
        for loc in self.locations:
            report += self._format_header(f"LOCATION: {loc}", level=1)
            
            loc_data = self.df[self.df['location'] == loc]
            report += f"Total bins in {loc}: {len(loc_data)}\n"
            
            for tax_level in self.tax_levels:
                report += self._format_header(f"Taxonomic Level: {tax_level.upper()}", level=2)
                
                organisms = set(loc_data[tax_level].unique()) - {"Unclassified", "None"}
                
                report += f"Total unique {tax_level}s in {loc}: {len(organisms)}\n"
                for org in sorted(organisms):
                    count = len(loc_data[loc_data[tax_level] == org])
                    layers = loc_data[loc_data[tax_level] == org]['layer'].unique()
                    report += f"  • {org} ({count} bins, layers: {', '.join(sorted(layers))})\n"
        
        self._write_report("03_location_distribution.txt", report)
        return report
    
    def analyze_cross_location_comparison(self):
        """
        Compare organisms across locations.
        Identifies common, unique, and shared organisms between location pairs.
        """
        report = self._format_header("PART 4: CROSS-LOCATION COMPARISON")
        report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Analysis of {', '.join(self.locations)} locations.\n"
        
        for tax_level in self.tax_levels:
            report += self._format_header(f"TAXONOMIC LEVEL: {tax_level.upper()}", level=1)
            
            loc_organisms = {}
            for loc in self.locations:
                loc_data = self.df[self.df['location'] == loc]
                loc_organisms[loc] = set(loc_data[tax_level].unique()) - {"Unclassified", "None"}
            
            if len(self.locations) > 0:
                common_all_locs = loc_organisms[self.locations[0]]
                for loc in self.locations[1:]:
                    common_all_locs = common_all_locs & loc_organisms[loc]
                
                report += f"\nOrganisms COMMON across ALL locations ({', '.join(self.locations)}): {len(common_all_locs)}\n"
                for org in sorted(common_all_locs):
                    report += f"  • {org}\n"
                    for loc in self.locations:
                        count = len(self.df[(self.df['location'] == loc) & (self.df[tax_level] == org)])
                        report += f"      {loc}: {count} bins\n"
            
            report += f"\nOrganisms UNIQUE to each location:\n"
            for loc in self.locations:
                other_locs = set(self.locations) - {loc}
                organisms_in_others = set()
                for other_loc in other_locs:
                    organisms_in_others = organisms_in_others | loc_organisms[other_loc]
                
                unique_to_loc = loc_organisms[loc] - organisms_in_others
                report += f"\nUnique to {loc}: {len(unique_to_loc)}\n"
                for org in sorted(unique_to_loc):
                    count = len(self.df[(self.df['location'] == loc) & (self.df[tax_level] == org)])
                    report += f"  • {org} ({count} bins)\n"
            
            report += f"\nOrganisms shared between pairs:\n"
            for i, loc1 in enumerate(self.locations):
                for loc2 in self.locations[i+1:]:
                    shared = loc_organisms[loc1] & loc_organisms[loc2]
                    not_in_third = shared.copy()
                    for loc3 in self.locations:
                        if loc3 not in [loc1, loc2]:
                            not_in_third = not_in_third - loc_organisms[loc3]
                    
                    third_loc = [l for l in self.locations if l not in [loc1, loc2]][0]
                    report += f"\n{loc1} & {loc2} (not in {third_loc}): {len(not_in_third)}\n"
                    for org in sorted(not_in_third):
                        count1 = len(self.df[(self.df['location'] == loc1) & (self.df[tax_level] == org)])
                        count2 = len(self.df[(self.df['location'] == loc2) & (self.df[tax_level] == org)])
                        report += f"  • {org} ({loc1}: {count1}, {loc2}: {count2})\n"
        
        self._write_report("04_cross_location_comparison.txt", report)
        return report
    
    def generate_abundance_summary(self):
        """
        Generate summary statistics for bins and unique taxa per location and layer.
        """
        report = self._format_header("PART 5: ABUNDANCE SUMMARY BY LOCATION AND LAYER")
        report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "Overview of bins and taxonomic diversity.\n\n"
        
        summary_data = []
        
        for loc in self.locations:
            loc_data = self.df[self.df['location'] == loc]
            for layer in ["TOP", "BOTTOM"]:
                layer_data = loc_data[loc_data['layer'] == layer]
                if len(layer_data) > 0:
                    summary_data.append({
                        'Location': loc,
                        'Layer': layer,
                        'Total Bins': len(layer_data),
                        'Unique Phyla': len(set(layer_data['phylum'].unique()) - {"Unclassified", "None"}),
                        'Unique Classes': len(set(layer_data['class'].unique()) - {"Unclassified", "None"}),
                        'Unique Families': len(set(layer_data['family'].unique()) - {"Unclassified", "None"}),
                        'Unique Genera': len(set(layer_data['genus'].unique()) - {"Unclassified", "None"}),
                    })
        
        summary_df = pd.DataFrame(summary_data)
        report += summary_df.to_string(index=False)
        report += "\n\n" + self._format_header("SUMMARY INTERPRETATION", level=1)
        
        total_bins = len(self.df)
        total_locations = len(self.df['location'].unique())
        total_phyla = len(set(self.df['phylum'].unique()) - {"Unclassified", "None"})
        
        report += f"\nDataset Overview:\n"
        report += f"  • Total bins analyzed: {total_bins}\n"
        report += f"  • Total locations: {total_locations}\n"
        report += f"  • Total unique phyla: {total_phyla}\n"
        report += f"  • Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        self._write_report("05_abundance_summary.txt", report)
        return report
    
    def generate_comprehensive_report(self):
        """
        Generate all analysis reports in sequence.
        """
        print("\nGenerating comprehensive analysis reports...\n")
        
        reports = {
            "Layer Distribution": self.analyze_layer_distribution(),
            "Cross-Layer Summary": self.analyze_cross_layer_summary(),
            "Location Distribution": self.analyze_location_distribution(),
            "Cross-Location Comparison": self.analyze_cross_location_comparison(),
            "Abundance Summary": self.generate_abundance_summary(),
        }
        
        return reports
    
    def generate_master_report(self):
        """
        Generate a comprehensive master report combining all analyses.
        """
        master_report = self._format_header("COMPREHENSIVE TAXONOMIC ANALYSIS - MASTER REPORT")
        master_report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        master_report += f"Source file: {self.tsv_file}\n"
        master_report += f"Output directory: {self.output_dir}\n"
        
        master_report += self._format_header("EXECUTIVE SUMMARY", level=1)
        master_report += f"\nTotal bins analyzed: {len(self.df)}\n"
        master_report += f"Locations: {', '.join(sorted(self.df['location'].unique()))}\n"
        master_report += f"Layers: {', '.join(sorted(self.df['layer'].unique()))}\n"
        master_report += f"Taxonomic levels analyzed: {', '.join(self.tax_levels)}\n"
        
        master_report += "\nSamples per location:\n"
        for loc in self.locations:
            count = len(self.df[self.df['location'] == loc])
            master_report += f"  • {loc}: {count} bins\n"
        
        master_report += "\nSamples per layer:\n"
        for layer in ["TOP", "BOTTOM"]:
            count = len(self.df[self.df['layer'] == layer])
            master_report += f"  • {layer}: {count} bins\n"
        
        master_report += self._format_header("GENERATED REPORTS", level=1)
        master_report += "\nThe following detailed reports have been generated:\n"
        master_report += "  1. 01_layer_distribution_analysis.txt - Detailed layer-wise analysis per location\n"
        master_report += "  2. 02_cross_layer_summary.txt - Global layer comparison\n"
        master_report += "  3. 03_location_distribution.txt - Complete taxonomic profiles per location\n"
        master_report += "  4. 04_cross_location_comparison.txt - Organism distribution across locations\n"
        master_report += "  5. 05_abundance_summary.txt - Statistical overview\n"
        
        master_report += self._format_header("DATA QUALITY NOTES", level=1)
        unclassified_bins = len(self.df[self.df['domain'] == 'Unclassified'])
        unclassified_pct = (unclassified_bins / len(self.df)) * 100 if len(self.df) > 0 else 0
        master_report += f"\nUnclassified bins: {unclassified_bins} ({unclassified_pct:.1f}%)\n"
        master_report += f"Classified bins: {len(self.df) - unclassified_bins} ({100-unclassified_pct:.1f}%)\n"
        
        self._write_report("00_master_report.txt", master_report)
        return master_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Comprehensive Taxonomic Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_results.py all_samples_merged.tsv
  python compare_results.py all_samples_merged.tsv --output custom_reports
  python compare_results.py --help
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the merged taxonomy TSV file"
    )
    parser.add_argument(
        "-o", "--output",
        default="taxonomy_reports",
        help="Output directory for report files (default: taxonomy_reports)"
    )
    
    args = parser.parse_args()
    
    # Verify input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found!")
        exit(1)
    
    print("="*80)
    print("COMPREHENSIVE TAXONOMIC ANALYSIS")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize analyzer
    analyzer = TaxonomyAnalyzer(args.input_file, output_dir=args.output)
    
    # Generate master report
    analyzer.generate_master_report()
    
    # Generate all detailed reports
    reports = analyzer.generate_comprehensive_report()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll reports have been saved to: {analyzer.output_dir}/")
    print("\nGenerated files:")
    print("00_master_report.txt")
    print("01_layer_distribution_analysis.txt")
    print("02_cross_layer_summary.txt")
    print("03_location_distribution.txt")
    print("04_cross_location_comparison.txt")
    print("05_abundance_summary.txt")
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
