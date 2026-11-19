
import joblib
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Load saved Logistic Regression pipeline
model = joblib.load("models/logistic_regression.joblib")

# Load test data
test_df = pd.read_csv("data/processed/test.csv")

X_test = test_df.drop(columns=["Churn"])
y_test = test_df["Churn"]

# Predict churn probabilities
probabilities = model.predict_proba(X_test)[:, 1]

print("\n========== THRESHOLD COMPARISON ==========")

for threshold in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:

    predictions = (probabilities >= threshold).astype(int)

    precision = precision_score(
        y_test, predictions, zero_division=0
    )

    recall = recall_score(
        y_test, predictions, zero_division=0
    )

    f1 = f1_score(
        y_test, predictions, zero_division=0
    )

    print(f"\nThreshold: {threshold}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

# Detailed report at threshold 0.40
chosen_threshold = 0.40

predictions = (
    probabilities >= chosen_threshold
).astype(int)

print("\n========== SELECTED THRESHOLD: 0.40 ==========")

print(classification_report(
    y_test,
    predictions,
    target_names=["No Churn", "Churn"]
))

print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))
