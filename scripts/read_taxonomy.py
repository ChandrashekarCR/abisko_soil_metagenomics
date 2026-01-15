import os 
import pandas as pd
import numpy as np
import argparse


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

    def read_genome_binning(self,bin_df):
        df = pd.read_csv(bin_df,sep='\t')

        # Select columns that start with Depth
        abundance_cols = [col for col in df.columns if col.startswith('Depth ')]
        # Conver to relative sequence abundance (RSA)
        df[abundance_cols] = df[abundance_cols].div(df[abundance_cols].sum(axis=0),axis=1)
        abundace_matrix = df[['bin'] + abundance_cols]

        return abundace_matrix



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_taxonompy.py',
                                     description='A script to read the taxonomy classificaiton given by the GTDB-Tk database.',
                                     usage='python3 read_taxonomy.py -i <gtdbtk file>')
    parser.add_argument('-i','--input_file',dest='gtdbtk_file',help='Path to the GTDB-tk file generated after running the NF-CORE/MAG pipeline')
    parser.add_argument('-b','--bin_file',dest='bins_file',help='Path to the bins file generated after running the NF-CORE/MAG pipeline')


    args = parser.parse_args()

    tax_df = Taxonomy(args.gtdbtk_file)

    merged_df = pd.merge(tax_df.convert_to_taxonomy_columns(), 
                        tax_df.read_genome_binning(args.bins_file),
                        on='bin')
    print(merged_df)
                        
