import pandas as pd

# Create a sample DataFrame
data = {"A": [55, None], "AAL": [55, None], "SAN.PA": [55, 55]}
index = pd.to_datetime(["1999-01-04", "1999-01-05"])
df = pd.DataFrame(data, index=index)

print("Original DataFrame:")
print(df)

# Define the column to check
column_to_check = "SAN.PA"

# Create a mask where the specified column is not NaN and all other columns are NaN
mask = df[column_to_check].notna() & df.drop(columns=[column_to_check]).isna().all(
    axis=1
)

# Drop rows that meet the condition
df_cleaned = df[~mask]

print("\nDataFrame after dropping rows:")
print(df_cleaned)
