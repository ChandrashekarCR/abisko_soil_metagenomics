import os 
import pandas as pd
import numpy as np
import argparse
import seaborn as sns
import matplotlib.pyplot as plt


class Taxonomy:
    def __init__(self,in_df):
        self.in_df = in_df

    def read_dataframe(self):
        """
        Docstring for read_dataframe
        
        :param self: Description
        """
        df = pd.read_csv(self.in_df, sep = '\t')
        # Remove NaN values in clasification column
        df = df.dropna(subset=['classification'],axis=0)
        return df
    
    def convert_to_taxonomy_columns(self):
        """
        Docstring for convert_to_taxonomy_columns
        
        :param self: Description
        """
        df = self.read_dataframe()
        # Split classifcaiton string
        tax_split = df['classification'].str.split(';',expand=True)
        tax_split.columns = ['domain','phylum','class','order','family','genus','species']
        # Remove prefix
        for col in tax_split.columns:
            tax_split[col] = tax_split[col].str.replace(r'^[a-z]__', '', regex=True)
        # Concatenate with original dataframe
        new_df = pd.concat([df['user_genome'], tax_split.iloc[:,:-1]], axis=1)
        new_df = new_df.rename(columns={'user_genome':'bin'})

        return new_df

    def read_genome_binning(self,bin_df,convert_to_rsa=False):
        df = pd.read_csv(bin_df,sep='\t')

        # Select columns that start with Depth
        abundance_cols = [col for col in df.columns if col.startswith('Depth ')]
        
        if convert_to_rsa:
            # Convert to relative sequence abundance (RSA)
            df = df.fillna(0)
            df[abundance_cols] = df[abundance_cols].div(df[abundance_cols].sum(axis=0),axis=1)
        abundace_matrix = df[['bin'] + abundance_cols]

        return abundace_matrix

    def create_taxonomic_abundance_plot(self, merged_df, taxonomic_level, output_dir='plots', 
                                       remove_unclassified=False, layer_filter=None, figsize=(14, 8)):
        """
        Create publication-quality stacked bar plot for a given taxonomic level.
        
        :param merged_df: Merged dataframe with taxonomy and abundance data
        :param taxonomic_level: Taxonomic level to plot ('domain', 'phylum', 'class', 'order', 'family', 'genus')
        :param output_dir: Directory to save plots
        :param remove_unclassified: Whether to remove unclassified taxa
        :param layer_filter: Filter samples by layer ('TOP', 'BOT', or None for all)
        :param figsize: Figure size tuple
        """
        # Set publication-quality style
        sns.set_style("whitegrid")
        sns.set_context("paper", font_scale=1.5)
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.linewidth'] = 1.5
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get abundance columns
        abundance_cols = [col for col in merged_df.columns if col.startswith('Depth')]
        
        # Filter by layer if specified
        if layer_filter:
            abundance_cols = [col for col in abundance_cols if layer_filter in col]
        
        # Group by taxonomic level
        taxa_abundance = merged_df.groupby(taxonomic_level)[abundance_cols].sum()
        
        # Remove unclassified if requested
        if remove_unclassified and "Unclassified" in taxa_abundance.index:
            taxa_abundance = taxa_abundance.drop("Unclassified")
        
        # Ensure "Unclassified" is always last (for legend order)
        if "Unclassified" in taxa_abundance.index:
            unclassified_row = taxa_abundance.loc[["Unclassified"]]
            taxa_abundance = pd.concat([
                taxa_abundance.drop("Unclassified"),
                unclassified_row
            ])
    
        # Assign colors, always set "Unclassified" to grey
        other_taxa = [taxon for taxon in taxa_abundance.index if taxon != "Unclassified"]
    
        if len(other_taxa) <= 10:
            colors = sns.color_palette("tab10", len(other_taxa))
        elif len(other_taxa) <= 20:
            colors = sns.color_palette("tab20", len(other_taxa))
        else:
            colors = sns.color_palette("husl", len(other_taxa))
    
        # Add grey for "Unclassified" at the end
        if "Unclassified" in taxa_abundance.index:
            colors = list(colors) + ["#BDBDBD"]  # grey
    
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot
        taxa_abundance.T.plot(
            kind='bar', stacked=True, ax=ax, color=colors,
            width=0.8, edgecolor='white', linewidth=0.5
        )
        
        # Customize plot
        ax.set_ylabel('Relative Sequence Abundance (RSA)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Sample', fontsize=14, fontweight='bold')
        
        # Format x-axis labels
        labels = [label.get_text().replace('Depth ', '') for label in ax.get_xticklabels()]
        ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # Customize legend
        legend_title = taxonomic_level.capitalize()
        ax.legend(title=legend_title, bbox_to_anchor=(1.05, 1), loc='upper left', 
                 frameon=True, fancybox=False, shadow=False, ncol=1, fontsize=10)
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set y-axis limits
        ymax = taxa_abundance.T.sum(axis=1).max()
        ax.set_ylim(0, ymax*1.05)
        
        # Add title
        title_parts = [f"{taxonomic_level.capitalize()}-level Taxonomic Composition"]
        if remove_unclassified:
            title_parts.append("(Unclassified removed)")
        if layer_filter:
            title_parts.append(f"({layer_filter} layer)")
        ax.set_title(' '.join(title_parts), fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Generate filename
        filename_parts = [taxonomic_level]
        if remove_unclassified:
            filename_parts.append('no_unclassified')
        if layer_filter:
            filename_parts.append(layer_filter.lower())
        filename = '_'.join(filename_parts) + '.png'
        
        # Save figure
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Saved plot: {output_path}")
        
        plt.close()

    def generate_all_plots(self, merged_df, output_dir='plots'):
        """
        Generate all requested publication-quality plots.
        
        :param merged_df: Merged dataframe with taxonomy and abundance data
        :param output_dir: Directory to save plots
        """
        taxonomic_levels = ['domain', 'phylum', 'class', 'order', 'family', 'genus']
        
        print("Generating publication-quality plots...")
        print("=" * 60)
        
        # 1. All taxa with unclassified (all samples)
        print("\n1. Generating plots with unclassified taxa (all samples)...")
        for level in taxonomic_levels:
            self.create_taxonomic_abundance_plot(merged_df, level, output_dir, 
                                                remove_unclassified=False, layer_filter=None)
        
        # 2. All taxa without unclassified (all samples)
        print("\n2. Generating plots without unclassified taxa (all samples)...")
        for level in taxonomic_levels:
            self.create_taxonomic_abundance_plot(merged_df, level, output_dir, 
                                                remove_unclassified=True, layer_filter=None)
        
        # 3. Without unclassified - TOP layer only
        print("\n3. Generating plots without unclassified taxa (TOP layer)...")
        for level in taxonomic_levels:
            self.create_taxonomic_abundance_plot(merged_df, level, output_dir, 
                                                remove_unclassified=True, layer_filter='TOP')
        
        # 4. Without unclassified - BOT layer only
        print("\n4. Generating plots without unclassified taxa (BOTTOM layer)...")
        for level in taxonomic_levels:
            self.create_taxonomic_abundance_plot(merged_df, level, output_dir, 
                                                remove_unclassified=True, layer_filter='BOT')
        
        print("\n" + "=" * 60)
        print(f"All plots generated successfully in '{output_dir}/' directory")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_taxonompy.py',
                                     description='A script to read the taxonomy classificaiton given by the GTDB-Tk database and generate publication-quality plots.',
                                     usage='python3 read_taxonomy.py -i <gtdbtk file> -b <bins file> -o <output_dir>')
    parser.add_argument('-i','--input_file',dest='gtdbtk_file',required=True,
                       help='Path to the GTDB-tk file generated after running the NF-CORE/MAG pipeline')
    parser.add_argument('-b','--bin_file',dest='bins_file',required=True,
                       help='Path to the bins file generated after running the NF-CORE/MAG pipeline')
    parser.add_argument('-o','--output_dir',dest='output_dir',default='plots',
                       help='Directory to save output plots (default: plots)')

    args = parser.parse_args()

    # Initialize Taxonomy object
    tax = Taxonomy(args.gtdbtk_file)
    
    # Process data
    print("Reading and processing taxonomy data...")
    tax_df = tax.convert_to_taxonomy_columns().replace('', 'Unclassified')
    
    print("Reading and processing binning data...")
    bin_df = tax.read_genome_binning(args.bins_file, convert_to_rsa=True)
    
    print("Merging taxonomy and abundance data...")
    merged_df = pd.merge(tax_df, bin_df, on='bin', how='outer')
    
    # Fill missing taxonomy with "Unclassified"
    for col in ["domain", "phylum", "class", "order", "family", "genus"]:
        merged_df[col] = merged_df[col].fillna("Unclassified")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    print(f"Total bins in bin_df: {len(bin_df)}")
    print(f"Bins with taxonomy: {len(tax_df)}")
    print(f"Bins in merged_df: {len(merged_df)}")
    
    abundance_cols = [col for col in merged_df.columns if col.startswith('Depth')]
    print(f"\nNumber of samples: {len(abundance_cols)}")
    print("\nSum of RSA per sample (should be 1.0):")
    print(merged_df[abundance_cols].sum(axis=0))
    
    bins_without_tax = set(bin_df['bin']) - set(tax_df['bin'])
    print(f"\nNumber of bins without taxonomy: {len(bins_without_tax)}")
    
    if len(bins_without_tax) > 0:
        missing_abundance = bin_df[bin_df['bin'].isin(bins_without_tax)][abundance_cols].sum(axis=0)
        print("\nAbundance from bins without taxonomy:")
        print(missing_abundance)
    
    # Generate all plots
    tax.generate_all_plots(merged_df, args.output_dir)


"""
python3 scripts/read_taxonomy.py -i abisko_results/kj_results/Taxonomy/GTDB-Tk/gtdbtk_summary.tsv -b abisko_results/kj_results/GenomeBinning/bin_summary.tsv -o abisko_results/kj_results/plots/

"""