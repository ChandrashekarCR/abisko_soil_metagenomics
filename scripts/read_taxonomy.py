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
        #df = df.dropna(subset=['classification'])
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
        df = pd.concat([df.reset_index(drop=True), tax_split], axis=1)
        df = df[tax_split.columns]
        return df

    def read_genome_binning(self):
        df = pd.read_csv(self.in_df,sep='\t')

        return df[['bin', 'Depth KJ_1_BOTTOM', 'Input_file', 'Dataset', 'user_genome', 'classification']]



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='read_taxonompy.py',
                                     description='A script to read the taxonomy classificaiton given by the GTDB-Tk database.',
                                     usage='python3 read_taxonomy.py -i <gtdbtk file>')
    parser.add_argument('-i','--input_file',dest='gtdbtk_file',help='Path to the GTDB-tk file generated after running the NF-CORE/MAG pipeline')


    args = parser.parse_args()

    tax_df = Taxonomy(args.gtdbtk_file)

    print(tax_df.read_dataframe()['user_genome'].to_list())
    #print(tax_df.convert_to_taxonomy_columns())

    #print(tax_df.read_genome_binning())