import pandas as pd

# Step 1: Read the JSON file into a Pandas DataFrame
df = pd.read_json('example.json')

# Step 2: Convert any list columns to strings
df = df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)

# Step 3: Convert DataFrame to Parquet file
df.to_parquet('example.parquet', engine='pyarrow')
