
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# File paths
DATA_PATH = Path("data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv")
REPORT_PATH = Path("reports")
REPORT_PATH.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Clean TotalCharges
df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"].astype(str).str.strip().replace("", pd.NA),
    errors="coerce"
)

# Create numerical target for analysis
df["ChurnFlag"] = df["Churn"].map({"No": 0, "Yes": 1})

sns.set_theme(style="whitegrid")

print("\n========== EDA SUMMARY ==========")

print("\nChurn percentage:")
print(df["Churn"].value_counts(normalize=True) * 100)

print("\nAverage tenure by churn:")
print(df.groupby("Churn")["tenure"].mean())

print("\nAverage monthly charges by churn:")
print(df.groupby("Churn")["MonthlyCharges"].mean())

print("\nAverage total charges by churn:")
print(df.groupby("Churn")["TotalCharges"].mean())

print("\nMissing TotalCharges:", df["TotalCharges"].isna().sum())

# 1. Churn distribution
plt.figure(figsize=(7, 5))
sns.countplot(data=df, x="Churn", hue="Churn")
plt.title("Customer Churn Distribution")
plt.xlabel("Churn")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig(REPORT_PATH / "churn_distribution.png")
plt.show()

# 2. Churn rate by categorical features
categorical_features = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "InternetService",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "TechSupport",
    "OnlineSecurity"
]

for column in categorical_features:
    churn_rate = (
        df.groupby(column, observed=False)["ChurnFlag"]
        .mean()
        .mul(100)
        .reset_index(name="ChurnRate")
    )

    plt.figure(figsize=(9, 5))
    sns.barplot(data=churn_rate, x=column, y="ChurnRate")
    plt.title(f"Churn Rate by {column}")
    plt.xlabel(column)
    plt.ylabel("Churn Rate (%)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(REPORT_PATH / f"churn_by_{column}.png")
    plt.show()

# 3. Tenure distribution by churn
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="Churn", y="tenure", hue="Churn")
plt.title("Customer Tenure vs Churn")
plt.xlabel("Churn")
plt.ylabel("Tenure (Months)")
plt.tight_layout()
plt.savefig(REPORT_PATH / "tenure_vs_churn.png")
plt.show()

# 4. Monthly charges vs churn
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="Churn", y="MonthlyCharges", hue="Churn")
plt.title("Monthly Charges vs Churn")
plt.xlabel("Churn")
plt.ylabel("Monthly Charges")
plt.tight_layout()
plt.savefig(REPORT_PATH / "monthly_charges_vs_churn.png")
plt.show()

# 5. Total charges vs churn
plt.figure(figsize=(8, 5))
sns.boxplot(
    data=df.dropna(subset=["TotalCharges"]),
    x="Churn",
    y="TotalCharges",
    hue="Churn"
)
plt.title("Total Charges vs Churn")
plt.xlabel("Churn")
plt.ylabel("Total Charges")
plt.tight_layout()
plt.savefig(REPORT_PATH / "total_charges_vs_churn.png")
plt.show()

# 6. Correlation heatmap for numerical features
numerical_df = df[
    ["SeniorCitizen", "tenure", "MonthlyCharges",
     "TotalCharges", "ChurnFlag"]
]

plt.figure(figsize=(9, 6))
sns.heatmap(
    numerical_df.corr(),
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(REPORT_PATH / "correlation_heatmap.png")
plt.show()


# 7. Detailed churn analysis by customer category

print("\n========== CHURN RATE BY CATEGORY ==========")

features = [
    "Contract",
    "PaymentMethod",
    "InternetService",
    "TechSupport",
    "OnlineSecurity",
    "PaperlessBilling",
    "SeniorCitizen",
    "Partner",
    "Dependents"
]

for column in features:
    result = (
        df.groupby(column, dropna=False)["ChurnFlag"]
        .agg(["count", "mean"])
    )

    result["ChurnRate (%)"] = result["mean"] * 100

    print(f"\n--- {column} ---")
    print(result[["count", "ChurnRate (%)"]].round(2))

# 8. Analyze missing TotalCharges records

print("\n========== MISSING TOTAL CHARGES RECORDS ==========")

print(
    df[df["TotalCharges"].isna()][
        ["customerID", "tenure", "MonthlyCharges", "TotalCharges", "Churn"]
    ]
)

# 9. Churn by tenure group

df["TenureGroup"] = pd.cut(
    df["tenure"],
    bins=[-1, 12, 24, 48, 72],
    labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"]
)

print("\n========== CHURN BY TENURE GROUP ==========")

print(
    df.groupby("TenureGroup", observed=False)["ChurnFlag"]
    .agg(["count", "mean"])
    .assign(ChurnRate=lambda x: x["mean"] * 100)
    .round(2)
)

print("\nEDA completed successfully!")
print("Visualizations saved in the reports folder.")
