
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from fastapi import FastAPI, HTTPException, Query

from src.recommendations import generate_recommendations


# ==========================================
# 1. PATHS AND CONFIGURATION
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT_DIR / "models" / "random_forest_tuned.joblib"
TRAIN_PATH = ROOT_DIR / "data" / "processed" / "train.csv"
TEST_PATH = ROOT_DIR / "data" / "processed" / "test.csv"

LOW_RISK_LIMIT = 0.30
HIGH_RISK_LIMIT = 0.60

FEATURE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges"
]


# ==========================================
# 2. FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="ChurnGuard API",
    description="Customer Churn Prediction and Retention Analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# 3. LOAD MODEL AND TRAINING REFERENCE
# ==========================================

print("Loading ChurnGuard model...")

model = joblib.load(MODEL_PATH)

train_df = pd.read_csv(TRAIN_PATH)

high_charge_limit = float(
    train_df["MonthlyCharges"].median()
)

print("Model loaded successfully.")
print("High monthly charge reference:", high_charge_limit)


# ==========================================
# 4. CUSTOMER INPUT VALIDATION
# ==========================================

class CustomerInput(BaseModel):

    gender: Literal["Female", "Male"]

    SeniorCitizen: int = Field(ge=0, le=1)

    Partner: Literal["Yes", "No"]
    Dependents: Literal["Yes", "No"]

    tenure: int = Field(ge=0, le=100)

    PhoneService: Literal["Yes", "No"]

    MultipleLines: Literal[
        "Yes", "No", "No phone service"
    ]

    InternetService: Literal[
        "DSL", "Fiber optic", "No"
    ]

    OnlineSecurity: Literal[
        "Yes", "No", "No internet service"
    ]

    OnlineBackup: Literal[
        "Yes", "No", "No internet service"
    ]

    DeviceProtection: Literal[
        "Yes", "No", "No internet service"
    ]

    TechSupport: Literal[
        "Yes", "No", "No internet service"
    ]

    StreamingTV: Literal[
        "Yes", "No", "No internet service"
    ]

    StreamingMovies: Literal[
        "Yes", "No", "No internet service"
    ]

    Contract: Literal[
        "Month-to-month",
        "One year",
        "Two year"
    ]

    PaperlessBilling: Literal["Yes", "No"]

    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]

    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float = Field(ge=0)


# ==========================================
# 5. HELPER FUNCTIONS
# ==========================================

def get_risk_level(probability):

    if probability >= HIGH_RISK_LIMIT:
        return "High"

    elif probability >= LOW_RISK_LIMIT:
        return "Medium"

    return "Low"


def analyze_customer(customer):

    customer_data = customer.model_dump()

    # Maintain the exact training feature order.
    input_df = pd.DataFrame(
        [customer_data],
        columns=FEATURE_COLUMNS
    )

    probability = float(
        model.predict_proba(input_df)[0, 1]
    )

    risk = get_risk_level(probability)

    priority, recommendations = generate_recommendations(
        customer_data,
        probability,
        high_charge_limit
    )

    return {
        "churn_probability": round(probability, 4),
        "churn_percentage": round(probability * 100, 2),
        "risk_level": risk,
        "retention_priority": priority,
        "recommendations": recommendations
    }


# ==========================================
# 6. ROOT ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Welcome to ChurnGuard API",
        "status": "running",
        "version": "1.0.0"
    }


# ==========================================
# 7. HEALTH ENDPOINT
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_name": "Tuned Random Forest"
    }


# ==========================================
# 8. INDIVIDUAL PREDICTION
# ==========================================

@app.post("/predict")
def predict(customer: CustomerInput):

    try:
        return analyze_customer(customer)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# 9. RETENTION RECOMMENDATIONS
# ==========================================

@app.post("/recommend")
def recommend(customer: CustomerInput):

    try:
        result = analyze_customer(customer)

        return {
            "risk_level": result["risk_level"],
            "retention_priority": result["retention_priority"],
            "recommendations": result["recommendations"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# 10. BATCH PREDICTION
# ==========================================

@app.post("/predict/batch")
def predict_batch(customers: list[CustomerInput]):

    if not customers:
        raise HTTPException(
            status_code=400,
            detail="At least one customer is required."
        )

    if len(customers) > 500:
        raise HTTPException(
            status_code=400,
            detail="Maximum 500 customers per request."
        )

    try:
        results = [
            analyze_customer(customer)
            for customer in customers
        ]

        return {
            "total_customers": len(results),
            "risk_summary": {
                "High": sum(
                    r["risk_level"] == "High" for r in results
                ),
                "Medium": sum(
                    r["risk_level"] == "Medium" for r in results
                ),
                "Low": sum(
                    r["risk_level"] == "Low" for r in results
                )
            },
            "predictions": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# 11. ANALYTICS SUMMARY
# ==========================================

@app.get("/analytics/summary")
def analytics_summary():

    try:
        test_df = pd.read_csv(TEST_PATH)

        X_test = test_df[FEATURE_COLUMNS]

        probabilities = model.predict_proba(X_test)[:, 1]

        risk_levels = [
            get_risk_level(float(p))
            for p in probabilities
        ]

        risk_counts = pd.Series(
            risk_levels
        ).value_counts()

        return {
            "total_customers": len(X_test),
            "high_risk": int(risk_counts.get("High", 0)),
            "medium_risk": int(risk_counts.get("Medium", 0)),
            "low_risk": int(risk_counts.get("Low", 0)),
            "average_churn_probability": round(
                float(probabilities.mean()), 4
            ),
            "high_risk_percentage": round(
                float((probabilities >= HIGH_RISK_LIMIT).mean() * 100),
                2
            )
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get("/customers")
def get_customers(
    search: str = Query(default=""),
    risk: str = Query(default="All"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        customers_df = pd.read_csv(TEST_PATH)

        X = customers_df[FEATURE_COLUMNS]
        probabilities = model.predict_proba(X)[:, 1]

        records = []

        for index, (_, customer) in enumerate(customers_df.iterrows()):
            probability = float(probabilities[index])

            records.append({
                "customer_id": f"CUST-{index + 1:04d}",
                "tenure": int(customer["tenure"]),
                "contract": customer["Contract"],
                "monthly_charges": float(customer["MonthlyCharges"]),
                "churn_probability": round(probability, 4),
                "churn_percentage": round(probability * 100, 2),
                "risk_level": get_risk_level(probability),
            })

        if search:
            search_text = search.lower()

            records = [
                customer for customer in records
                if search_text in customer["customer_id"].lower()
                or search_text in str(customer["contract"]).lower()
            ]

        if risk != "All":
            if risk not in ["High", "Medium", "Low"]:
                raise HTTPException(
                    status_code=400,
                    detail="Risk must be High, Medium, Low, or All."
                )

            records = [
                customer for customer in records
                if customer["risk_level"] == risk
            ]

        total = len(records)
        paginated_records = records[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "customers": paginated_records,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/insights")
def get_analytics_insights():
    try:
        df = pd.read_csv(TEST_PATH)

        def calculate_churn_rate(column):
            result = (
                df.groupby(column, dropna=False)
                .agg(
                    customers=("Churn", "count"),
                    churned=("Churn", "sum")
                )
                .reset_index()
            )

            result["churn_rate"] = (
                result["churned"] / result["customers"] * 100
            ).round(2)

            result[column] = result[column].fillna("Unknown").astype(str)

            return result.rename(columns={column: "category"}).to_dict(
                orient="records"
            )

        tenure_bins = [0, 12, 24, 48, 72, float("inf")]
        tenure_labels = [
            "0–12 months",
            "13–24 months",
            "25–48 months",
            "49–72 months",
            "73+ months"
        ]

        df["TenureGroup"] = pd.cut(
            df["tenure"],
            bins=tenure_bins,
            labels=tenure_labels,
            include_lowest=True
        )

        probabilities = model.predict_proba(df[FEATURE_COLUMNS])[:, 1]

        risk_counts = {
            "High": int((probabilities >= HIGH_RISK_LIMIT).sum()),
            "Medium": int(
                (
                    (probabilities >= LOW_RISK_LIMIT)
                    & (probabilities < HIGH_RISK_LIMIT)
                ).sum()
            ),
            "Low": int((probabilities < LOW_RISK_LIMIT).sum())
        }

        return {
            "contract_churn": calculate_churn_rate("Contract"),
            "internet_churn": calculate_churn_rate("InternetService"),
            "tenure_churn": calculate_churn_rate("TenureGroup"),
            "payment_churn": calculate_churn_rate("PaymentMethod"),
            "risk_distribution": [
                {"category": key, "customers": value}
                for key, value in risk_counts.items()
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/feature-importance")
def get_feature_importance():
    shap_path = ROOT_DIR / "reports" / "shap_global_importance.csv"

    if not shap_path.exists():
        raise HTTPException(
            status_code=404,
            detail="SHAP feature importance file not found."
        )

    df = pd.read_csv(shap_path)

    # Normalize column names to handle different CSV formats
    df.columns = [
        col.strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    feature_col = "feature"
    importance_col = "mean_absolute_shap"

    if feature_col not in df.columns or importance_col not in df.columns:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected SHAP CSV columns: {list(df.columns)}"
        )

    df = df.sort_values(importance_col, ascending=False).head(15)

    return {
        "features": [
            {
                "category": str(row[feature_col]),
                "customers": float(row[importance_col])
            }
            for _, row in df.iterrows()
        ]
    }
