# ChurnGuard – Intelligent Customer Churn Prediction and Retention Analytics

ChurnGuard is a full-stack machine learning application that predicts customer churn, identifies customers at risk of leaving, explains model predictions using Explainable AI (SHAP), and provides actionable retention recommendations.

The application combines machine learning, explainable AI, data analytics, and web development to help businesses understand customer behaviour and make data-driven retention decisions.

## Live Application

- **Frontend:** https://churnguard-nu.vercel.app
- **Backend API:** https://churnguard-backend-x05n.onrender.com
- **API Documentation:** https://churnguard-backend-x05n.onrender.com/docs
- **GitHub Repository:** https://github.com/RakshithaG24/ChurnGuard

## Key Features

### 1. Customer Churn Prediction
- Predicts the probability of a customer leaving a service.
- Classifies customers into High, Medium, and Low risk categories.
- Accepts customer information through an interactive form.

### 2. Customer Analytics Dashboard
- Displays total customers analyzed.
- Shows high-risk customer counts.
- Visualizes predicted churn risk distribution.
- Provides an overview of customer retention insights.

### 3. Customer Management
- Displays customer records.
- Supports customer search and risk-based filtering.
- Helps identify customers requiring retention attention.

### 4. Explainable AI using SHAP
- Identifies important features influencing model predictions.
- Provides global feature importance.
- Helps interpret machine learning model behaviour.

### 5. Retention Recommendations
- Generates customer-specific retention suggestions.
- Uses customer attributes and predicted risk levels.
- Highlights potential actions for high-risk customers.

### 6. Analytics
- Visualizes churn patterns across:
  - Contract types
  - Internet service types
  - Customer tenure groups
  - Payment methods
- Displays model-based risk distribution and SHAP feature importance.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn, Recharts |
| Machine Learning | Scikit-learn, XGBoost |
| Explainable AI | SHAP |
| Backend | FastAPI, Uvicorn |
| Frontend | React, TypeScript, Vite |
| UI Icons | Lucide React |
| Model Persistence | Joblib |
| Deployment | Render, Vercel |
| Version Control | Git, GitHub |

## Machine Learning Workflow

1. Data collection using the IBM Telco Customer Churn dataset.
2. Exploratory Data Analysis (EDA).
3. Data cleaning and preprocessing.
4. Feature engineering and encoding.
5. Training multiple classification models.
6. Hyperparameter tuning using RandomizedSearchCV.
7. Model evaluation using classification metrics.
8. Churn probability threshold exploration.
9. Model interpretation using SHAP.
10. Generation of customer retention recommendations.

## Models Implemented

The project explores four classification algorithms:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost

A tuned Random Forest model is used by the deployed prediction API.

## Dataset

**IBM Telco Customer Churn Dataset**

- Total records: 7,043
- Original features: 21
- Target variable: Churn
- Training records: 5,634
- Testing records: 1,409

The dataset contains customer demographics, account information, service subscriptions, tenure, charges, and churn status.

## Model Evaluation

The initial baseline models were evaluated using Accuracy, Precision, Recall, F1-score, and ROC-AUC.

The tuned Random Forest achieved the highest cross-validation ROC-AUC among the tuned models.

The project also explores classification thresholds to understand the trade-off between precision and recall.

## Explainable AI

SHAP (SHapley Additive exPlanations) is used to understand the contribution of input features to model predictions.

Some of the important features identified include:

- Month-to-month contracts
- Customer tenure
- Fiber optic internet service
- Online security subscription
- Tech support subscription
- Electronic check payment method

Feature importance indicates model attribution, not necessarily causation.

## Project Structure

```text
ChurnGuard/
│
├── backend/
│   └── app/
│       └── main.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   └── components/
│   └── package.json
│
├── models/
│
├── reports/
│
├── src/
│   ├── preprocessing.py
│   ├── train_models.py
│   ├── tune_models.py
│   ├── explain_model.py
│   └── recommendations.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/RakshithaG24/ChurnGuard.git
cd ChurnGuard
```

### 2. Set up the Python environment

```bash
python -m venv .venv
```

Activate the environment on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
```

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome endpoint |
| GET | `/health` | Backend health check |
| POST | `/predict` | Predict customer churn |
| POST | `/recommend` | Generate retention recommendations |
| POST | `/predict/batch` | Batch customer predictions |
| GET | `/analytics/summary` | Dashboard summary |
| GET | `/analytics/insights` | Customer churn insights |
| GET | `/analytics/feature-importance` | SHAP feature importance |
| GET | `/customers` | Retrieve customer records |

For request and response schemas, visit the Swagger documentation.

## Deployment Architecture

- **Frontend:** React application deployed on Vercel.
- **Backend:** FastAPI application deployed on Render.
- **Communication:** REST API requests using Axios.
- **Machine Learning:** Serialized model loaded by the backend using Joblib.

## Future Enhancements

- Integrate PostgreSQL for persistent customer data storage.
- Add user authentication and role-based access.
- Introduce model monitoring and performance tracking.
- Improve model evaluation using an independent validation strategy.
- Add automated model retraining.
- Develop more advanced customer retention strategies.

## Author

**Rakshitha G.**

Information Science and Engineering

GitHub: https://github.com/RakshithaG24

---

*ChurnGuard – Turning customer data into actionable retention insights.*