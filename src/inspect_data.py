
import pandas as pd
from pathlib import Path

# Dataset location
DATA_PATH = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Load dataset
df = pd.read_csv(DATA_PATH)

# Basic information
print("\n========== DATASET OVERVIEW ==========")
print("Shape:", df.shape)
print("\nFirst 5 records:")
print(df.head())

# Column information
print("\n========== DATA TYPES ==========")
print(df.info())

# Statistical summary
print("\n========== STATISTICAL SUMMARY ==========")
print(df.describe(include="all").T)

# Missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# Check blank values
print("\n========== BLANK VALUES ==========")
for column in df.columns:
    if df[column].dtype == "object":
        blanks = df[column].astype(str).str.strip().eq("").sum()
        if blanks > 0:
            print(column, ":", blanks)

# Duplicate records
print("\n========== DUPLICATES ==========")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate customer IDs:", df["customerID"].duplicated().sum())

# Churn distribution
print("\n========== CHURN DISTRIBUTION ==========")
print(df["Churn"].value_counts())
print(df["Churn"].value_counts(normalize=True) * 100)

print("\nDataset inspection completed!")
