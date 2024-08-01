import pandas as pd

# Example DataFrame similar to the one you described
data = {
    'A': [64.401237, 66.039833, 65.544441, 66.592369, 66.735291],
    'AAL': [51.647556, 51.014019, 51.335667, 51.316177, 50.809349],
    'AAPL': [40.615891, 40.608822, 40.797443, 41.261940, 41.108673],
    'ABBV': [72.923515, 74.064651, 73.642288, 74.924225, 73.723808],
    'ABNB': [None, None, None, None, None],  # All NaN
    'ABT': [52.293575, 52.409203, 52.320259, 52.471474, 52.320259],
    'XOM': [62.133785, 63.354115, 63.441788, 63.390625, 63.675617],
    'XYL': [62.936825, 63.704250, 64.129562, 64.009354, 64.240486],
    'YUM': [72.576630, 72.514389, 73.252586, 73.679535, 73.804031],
    'ZBH': [114.517616, 115.311462, 115.145309, 116.289932, 116.511482],
    'ZBRA': [103.709999, 105.769997, 107.860001, 109.540001, 110.629997],
    'ZTS': [68.448692, 68.763412, 69.173538, 69.965111, 70.804382]
}
index = pd.date_range(start='2018-01-02', periods=5, freq='B')
df = pd.DataFrame(data, index=index)

print("Original DataFrame:")
print(df)

# Drop columns with all NaN values
df_cleaned = df.dropna(axis=1, how='all')

print("\nDataFrame after dropping columns with all NaN values:")
print(df_cleaned)