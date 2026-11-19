
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

# File paths
DATA_PATH = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

print("Original dataset shape:", df.shape)

# Step 1: Convert TotalCharges to numeric
df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"].astype(str).str.strip(),
    errors="coerce"
)

# Step 2: Verify missing values
print("\nMissing TotalCharges:", df["TotalCharges"].isna().sum())

# Missing TotalCharges should belong to new customers
missing_mask = df["TotalCharges"].isna()

if not (df.loc[missing_mask, "tenure"] == 0).all():
    raise ValueError("Unexpected missing TotalCharges values found.")

# Replace missing TotalCharges with 0
df["TotalCharges"] = df["TotalCharges"].fillna(0)

# Step 3: Remove customer identifier
df = df.drop(columns=["customerID"])

# Step 4: Convert target into binary values
df["Churn"] = df["Churn"].map({"No": 0, "Yes": 1})

if df["Churn"].isna().any():
    raise ValueError("Unexpected values found in Churn column.")

# Step 5: Separate features and target
X = df.drop(columns=["Churn"])
y = df["Churn"]

# Step 6: Split into training and testing datasets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Step 7: Recombine features and target for saving
train_data = X_train.copy()
train_data["Churn"] = y_train

test_data = X_test.copy()
test_data["Churn"] = y_test

# Step 8: Save processed datasets
train_data.to_csv(OUTPUT_PATH / "train.csv", index=False)
test_data.to_csv(OUTPUT_PATH / "test.csv", index=False)

# Step 9: Display results
print("\n========== PREPROCESSING SUMMARY ==========")

print("Training data shape:", X_train.shape)
print("Testing data shape:", X_test.shape)

print("\nTraining churn distribution:")
print(y_train.value_counts())
print(y_train.value_counts(normalize=True) * 100)

print("\nTesting churn distribution:")
print(y_test.value_counts())
print(y_test.value_counts(normalize=True) * 100)

print("\nMissing values after preprocessing:")
print(df.isnull().sum().sum())

print("\nSaved files:")
print("data/processed/train.csv")
print("data/processed/test.csv")

print("\nPreprocessing completed successfully!")
