import pandas as pd

df = pd.read_csv("dataset_refined_keywords2.csv")
df.to_parquet("dataset2.parquet")