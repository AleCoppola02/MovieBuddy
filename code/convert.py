import pandas as pd

df = pd.read_csv("dataset_refined_keywords3.csv")
df.to_parquet("dataset.parquet")