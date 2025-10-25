import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("aws_cost_optimization_dirty.csv")

# Remove duplicate rows
df = df.drop_duplicates()

# Standardize column names
df.columns = [col.strip().lower().replace(" ", "_").replace("(%)", "percent") for col in df.columns]

# Parse and standardize dates
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Lowercase service and region, strip spaces
df['service'] = df['service'].str.strip().str.lower()
df['region'] = df['region'].str.strip().str.lower()

# Convert numeric columns, coerce errors to NaN
for col in ['usage_hours', 'cpu_utilizationpercent', 'cost_usd']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Fill missing or invalid numeric values with 0 (or use .fillna(method) as needed)
df['usage_hours'] = df['usage_hours'].fillna(0)
df['cpu_utilizationpercent'] = df['cpu_utilizationpercent'].fillna(0)
df['cost_usd'] = df['cost_usd'].fillna(0)

# Drop unneeded columns
df = df.drop(columns=['notes', 'extra_column'], errors='ignore')

# Drop rows with missing date (optional)
df = df.dropna(subset=['date'])

# Save cleaned data
df.to_csv("aws_cost_optimization_cleaned.csv", index=False)