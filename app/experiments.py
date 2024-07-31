import pandas as pd

# Example data for df1
data1 = [1.794007, 1.713286, 1.736128, 1.722529, 1.789851]
# Example data for df2
data2 = [1.800007, 1.710286, 1.740128, 1.730529, 1.795851]

# Create DataFrames
d1 = pd.DataFrame(data1)
d2 = pd.DataFrame(data2)

print("TEST TEST TES D1")

# Print the combined DataFrame
print(d1)

df1 = d1.rename(columns={0: "values"})
df2 = d2.rename(columns={0: "values"})

print("TEST TEST TES DF1")

# Print the combined DataFrame
print(df1)

# Add category column
df1["category"] = "A"
df2["category"] = "B"

# Concatenate DataFrames
df_combined = pd.concat([df1, df2], ignore_index=True)

print("TEST TEST TEST")

# Print the combined DataFrame
print(df_combined)
