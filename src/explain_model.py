
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt

from pathlib import Path

# ==========================================
# 1. PATHS
# ==========================================

MODEL_PATH = Path("models/random_forest_tuned.joblib")
TRAIN_PATH = Path("data/processed/train.csv")
REPORT_PATH = Path("reports")

REPORT_PATH.mkdir(exist_ok=True)

# ==========================================
# 2. LOAD MODEL AND DATA
# ==========================================

print("Loading tuned Random Forest model...")

pipeline = joblib.load(MODEL_PATH)

train_df = pd.read_csv(TRAIN_PATH)

X_train = train_df.drop(columns=["Churn"])
y_train = train_df["Churn"]

print("Training data shape:", X_train.shape)

# ==========================================
# 3. SELECT A SAMPLE
# ==========================================

# SHAP can be computationally expensive.
# Use a representative sample for explanations.

X_sample = X_train.sample(
    n=min(300, len(X_train)),
    random_state=42
)

# ==========================================
# 4. TRANSFORM DATA
# ==========================================

print("\nTransforming customer features...")

preprocessor = pipeline.named_steps["preprocessor"]
classifier = pipeline.named_steps["classifier"]

X_transformed = preprocessor.transform(X_sample)

feature_names = preprocessor.get_feature_names_out()

if hasattr(X_transformed, "toarray"):
    X_transformed = X_transformed.toarray()

X_transformed = pd.DataFrame(
    X_transformed,
    columns=feature_names,
    index=X_sample.index
)

print("Transformed shape:", X_transformed.shape)

# ==========================================
# 5. CREATE SHAP EXPLAINER
# ==========================================

print("\nCalculating SHAP values...")

explainer = shap.TreeExplainer(classifier)

shap_values = explainer.shap_values(X_transformed)

# Handle binary classification output formats.
if isinstance(shap_values, list):
    positive_shap_values = shap_values[1]
elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
    positive_shap_values = shap_values[:, :, 1]
else:
    positive_shap_values = shap_values

# ==========================================
# 6. GLOBAL FEATURE IMPORTANCE
# ==========================================

print("\nGenerating global feature importance...")

shap.summary_plot(
    positive_shap_values,
    X_transformed,
    show=False,
    max_display=15
)

plt.tight_layout()
plt.savefig(
    REPORT_PATH / "shap_summary.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# ==========================================
# 7. FEATURE IMPORTANCE BAR PLOT
# ==========================================

shap.summary_plot(
    positive_shap_values,
    X_transformed,
    plot_type="bar",
    show=False,
    max_display=15
)

plt.tight_layout()
plt.savefig(
    REPORT_PATH / "shap_feature_importance.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# ==========================================
# 8. INDIVIDUAL CUSTOMER EXPLANATION
# ==========================================

print("\nGenerating individual customer explanation...")

customer_index = 0

customer = X_transformed.iloc[customer_index]

# Obtain the model's probability for churn.

churn_probability = classifier.predict_proba(
    X_transformed.iloc[[customer_index]].to_numpy()
)[0, 1]

print("Customer churn probability:", round(churn_probability, 4))

# Waterfall plot using the SHAP explanation object.
if hasattr(explainer, "expected_value"):
    base_value = explainer.expected_value

    if isinstance(base_value, (list, np.ndarray)):
        base_value = np.asarray(base_value).flatten()[-1]

    explanation = shap.Explanation(
        values=positive_shap_values[customer_index],
        base_values=base_value,
        data=customer.values,
        feature_names=feature_names
    )

    shap.plots.waterfall(
        explanation,
        max_display=15,
        show=False
    )

    plt.tight_layout()
    plt.savefig(
        REPORT_PATH / "shap_customer_explanation.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

# ==========================================
# 9. SAVE SHAP VALUES
# ==========================================

shap_df = pd.DataFrame(
    positive_shap_values,
    columns=feature_names,
    index=X_sample.index
)

shap_df.to_csv(
    REPORT_PATH / "shap_values.csv",
    index=True
)

# ==========================================
# 10. SUMMARY
# ==========================================

importance = pd.DataFrame({
    "Feature": feature_names,
    "Mean Absolute SHAP": np.abs(
        positive_shap_values
    ).mean(axis=0)
})

importance = importance.sort_values(
    by="Mean Absolute SHAP",
    ascending=False
)

print("\n========== TOP 15 CHURN FACTORS ==========")
print(importance.head(15).to_string(index=False))

importance.to_csv(
    REPORT_PATH / "shap_global_importance.csv",
    index=False
)

print("\nSHAP analysis completed successfully!")
print("Reports saved in:", REPORT_PATH)
