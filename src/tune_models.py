
import pandas as pd
import joblib

from pathlib import Path
from scipy.stats import randint, uniform

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


# ==========================================
# 1. PATHS AND TRAINING DATA
# ==========================================

TRAIN_PATH = Path("data/processed/train.csv")
MODEL_PATH = Path("models")
REPORT_PATH = Path("reports")

MODEL_PATH.mkdir(exist_ok=True)
REPORT_PATH.mkdir(exist_ok=True)

train_df = pd.read_csv(TRAIN_PATH)

X_train = train_df.drop(columns=["Churn"])
y_train = train_df["Churn"]

print("Training data shape:", X_train.shape)


# ==========================================
# 2. FEATURE IDENTIFICATION
# ==========================================

numerical_features = X_train.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

categorical_features = X_train.select_dtypes(
    include=["object", "category", "string"]
).columns.tolist()


# ==========================================
# 3. PREPROCESSING PIPELINE
# ==========================================

def create_preprocessor():

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    return ColumnTransformer(transformers=[
        ("num", numeric_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features)
    ])


# ==========================================
# 4. DEFINE MODELS AND SEARCH SPACES
# ==========================================

models = {

    "Logistic Regression": {
        "classifier": LogisticRegression(
            max_iter=3000,
            random_state=42
        ),
        "params": {
            "classifier__C": uniform(0.01, 10),
            "classifier__class_weight": [None, "balanced"]
        },
        "iterations": 10
    },

    "Decision Tree": {
        "classifier": DecisionTreeClassifier(
            random_state=42
        ),
        "params": {
            "classifier__max_depth": [None, 3, 5, 8, 12, 16],
            "classifier__min_samples_split": randint(2, 15),
            "classifier__min_samples_leaf": randint(1, 10),
            "classifier__criterion": ["gini", "entropy", "log_loss"],
            "classifier__class_weight": [None, "balanced"]
        },
        "iterations": 10
    },

    "Random Forest": {
        "classifier": RandomForestClassifier(
            random_state=42,
            n_jobs=1
        ),
        "params": {
            "classifier__n_estimators": randint(200, 501),
            "classifier__max_depth": [None, 8, 12, 16, 20],
            "classifier__min_samples_split": randint(2, 12),
            "classifier__min_samples_leaf": randint(1, 8),
            "classifier__max_features": ["sqrt", "log2"],
            "classifier__class_weight": [
                None, "balanced", "balanced_subsample"
            ]
        },
        "iterations": 10
    },

    "XGBoost": {
        "classifier": XGBClassifier(
            eval_metric="logloss",
            random_state=42,
            n_jobs=1
        ),
        "params": {
            "classifier__n_estimators": randint(200, 501),
            "classifier__learning_rate": uniform(0.02, 0.13),
            "classifier__max_depth": randint(3, 8),
            "classifier__subsample": uniform(0.7, 0.3),
            "classifier__colsample_bytree": uniform(0.7, 0.3),
            "classifier__min_child_weight": randint(1, 8),
            "classifier__gamma": uniform(0, 0.3),
            "classifier__reg_lambda": uniform(0.5, 3)
        },
        "iterations": 10
    }
}


# ==========================================
# 5. CROSS-VALIDATION CONFIGURATION
# ==========================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

results = []


# ==========================================
# 6. HYPERPARAMETER TUNING
# ==========================================

for model_name, config in models.items():

    print("\n" + "=" * 60)
    print("TUNING:", model_name)
    print("=" * 60)

    pipeline = Pipeline(steps=[
        ("preprocessor", create_preprocessor()),
        ("classifier", config["classifier"])
    ])

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=config["params"],
        n_iter=config["iterations"],
        scoring="roc_auc",
        cv=cv,
        random_state=42,
        n_jobs=-1,
        verbose=1,
        refit=True
    )

    search.fit(X_train, y_train)

    print("\nBest CV ROC-AUC:", round(search.best_score_, 4))
    print("Best Parameters:")
    print(search.best_params_)

    # Save optimized pipeline separately.
    filename = model_name.lower().replace(" ", "_")

    joblib.dump(
        search.best_estimator_,
        MODEL_PATH / f"{filename}_tuned.joblib"
    )

    results.append({
        "Model": model_name,
        "Best CV ROC-AUC": search.best_score_,
        "Best Parameters": str(search.best_params_)
    })


# ==========================================
# 7. SAVE TUNING RESULTS
# ==========================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="Best CV ROC-AUC",
    ascending=False
)

print("\n========== TUNING COMPARISON ==========")
print(results_df.to_string(index=False))

results_df.to_csv(
    REPORT_PATH / "hyperparameter_tuning_results.csv",
    index=False
)

print("\nHyperparameter tuning completed!")
print("Optimized models saved in:", MODEL_PATH)
print("Results saved in:", REPORT_PATH)
