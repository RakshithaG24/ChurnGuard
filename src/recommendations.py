from pathlib import Path
import joblib
import pandas as pd

# ==========================================
# 1. PATHS AND CONFIGURATION
# ==========================================

MODEL_PATH = Path("models/random_forest_tuned.joblib")
TRAIN_PATH = Path("data/processed/train.csv")
TEST_PATH = Path("data/processed/test.csv")
REPORT_PATH = Path("reports")

REPORT_PATH.mkdir(exist_ok=True)

# Provisional risk bands for dashboard display.
LOW_RISK_LIMIT = 0.30
HIGH_RISK_LIMIT = 0.60


# ==========================================
# 2. RETENTION RECOMMENDATION FUNCTION
# ==========================================


def generate_recommendations(customer, churn_probability, high_charge_limit):
    recommendations = []

    # Contract-related recommendation
    if customer["Contract"] == "Month-to-month":
        recommendations.append(
            "Offer a discount or incentive for switching "
            "to a long-term contract."
        )

    # Customer tenure
    if customer["tenure"] <= 12:
        recommendations.append(
            "Provide an onboarding incentive and regular "
            "follow-ups to improve early customer engagement."
        )

    # Online security
    if customer["OnlineSecurity"] == "No":
        recommendations.append("Offer an affordable online security package.")

    # Technical support
    if customer["TechSupport"] == "No":
        recommendations.append("Recommend a technical support package.")

    # Monthly charges
    if customer["MonthlyCharges"] > high_charge_limit:
        recommendations.append(
            "Review the customer's monthly bill and offer "
            "a suitable lower-cost plan if available."
        )

    # Payment method
    if customer["PaymentMethod"] == "Electronic check":
        recommendations.append(
            "Offer convenient automatic payment options "
            "and explain their benefits."
        )

    # Internet service
    if customer["InternetService"] == "Fiber optic":
        recommendations.append(
            "Review service satisfaction and internet "
            "performance with the customer."
        )

    # Backup services
    if customer["OnlineBackup"] == "No":
        recommendations.append("Offer an optional online backup package.")

    # If no specific recommendation is triggered
    if not recommendations:
        recommendations.append(
            "Maintain regular engagement and monitor customer satisfaction."
        )

    # Risk-based action priority
    if churn_probability >= HIGH_RISK_LIMIT:
        priority = "High"
        recommendations.insert(
            0,
            "Prioritize this customer for a retention "
            "follow-up by the customer success team.",
        )

    elif churn_probability >= LOW_RISK_LIMIT:
        priority = "Medium"
        recommendations.insert(
            0, "Schedule a proactive customer satisfaction check-in."
        )

    else:
        priority = "Low"
        recommendations.insert(0, "Continue regular customer engagement.")

    return priority, recommendations


def main():
    # ==========================================
    # 3. LOAD MODEL AND DATA
    # ==========================================

    print("Loading tuned Random Forest model...")

    model = joblib.load(MODEL_PATH)

    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    X_train = train_df.drop(columns=["Churn"])
    X_test = test_df.drop(columns=["Churn"])

    print("Customers to analyze:", len(X_test))

    # ==========================================
    # 4. DETERMINE HIGH CHARGE REFERENCE
    # ==========================================

    # Use the training data to establish the reference value.
    high_charge_limit = X_train["MonthlyCharges"].median()

    print("Training median monthly charge:", round(high_charge_limit, 2))

    # ==========================================
    # 5. PREDICT CHURN PROBABILITIES
    # ==========================================

    print("\nPredicting customer churn probabilities...")

    probabilities = model.predict_proba(X_test)[:, 1]

    # ==========================================
    # 6. GENERATE RECOMMENDATIONS
    # ==========================================

    results = []

    for index, (_, customer) in enumerate(X_test.iterrows()):
        probability = float(probabilities[index])

        if probability >= HIGH_RISK_LIMIT:
            risk = "High"

        elif probability >= LOW_RISK_LIMIT:
            risk = "Medium"

        else:
            risk = "Low"

        priority, recommendations = generate_recommendations(
            customer, probability, high_charge_limit
        )

        results.append({
            "Customer_Record": f"Test_Record_{index + 1:04d}",
            "Churn_Probability": round(probability, 4),
            "Risk_Level": risk,
            "Retention_Priority": priority,
            "Contract": customer["Contract"],
            "Tenure": customer["tenure"],
            "MonthlyCharges": customer["MonthlyCharges"],
            "Recommendations": " | ".join(recommendations),
        })

    # ==========================================
    # 7. SAVE RESULTS
    # ==========================================

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(by="Churn_Probability", ascending=False)

    output_path = REPORT_PATH / "retention_recommendations.csv"

    results_df.to_csv(output_path, index=False)

    # ==========================================
    # 8. DISPLAY SUMMARY
    # ==========================================

    print("\n========== CUSTOMER RISK SUMMARY ==========")

    print(
        results_df["Risk_Level"]
        .value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
    )

    print("\n========== TOP 10 HIGH-RISK CUSTOMERS ==========")

    print(results_df.head(10).to_string(index=False))

    print("\nRecommendations generated successfully!")
    print("Saved to:", output_path)


if __name__ == "__main__":
    main()