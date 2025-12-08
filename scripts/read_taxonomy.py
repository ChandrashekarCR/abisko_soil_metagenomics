import os 
import pandas as pd
import numpy as np


df = pd.read_csv("temp_results/Taxonomy/GTDB-Tk/gtdbtk_summary.tsv",sep='\t')

print(df.columns)

print(df[['classification']])