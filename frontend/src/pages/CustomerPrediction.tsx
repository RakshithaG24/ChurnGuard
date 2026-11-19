
import { useState, type FormEvent } from "react";
import axios from "axios";
import api from "../services/api";
import {
  BrainCircuit,
  AlertTriangle,
  CheckCircle,
  Loader2,
  RefreshCw,
  ServerCrash,
} from "lucide-react";

const initialForm = {
  gender: "Female",
  SeniorCitizen: 0,
  Partner: "Yes",
  Dependents: "No",
  tenure: 12,
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "Fiber optic",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: 85.5,
  TotalCharges: 1026,
};

type CustomerForm = typeof initialForm;

interface PredictionResult {
  churn_probability: number;
  churn_percentage: number;
  risk_level: "High" | "Medium" | "Low";
  retention_priority: string;
  recommendations: string[];
}

const CustomerPrediction = () => {
  const [form, setForm] = useState<CustomerForm>(initialForm);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateField = (
    field: keyof CustomerForm,
    value: string | number
  ) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));

    setError("");
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (loading) return;

    // Validate numeric inputs
    if (
      !Number.isInteger(form.SeniorCitizen) ||
      ![0, 1].includes(form.SeniorCitizen)
    ) {
      setError("Senior Citizen must be either 0 or 1.");
      return;
    }

    if (
      !Number.isInteger(form.tenure) ||
      form.tenure < 0 ||
      form.tenure > 100
    ) {
      setError("Tenure must be between 0 and 100 months.");
      return;
    }

    if (
      !Number.isFinite(form.MonthlyCharges) ||
      form.MonthlyCharges < 0
    ) {
      setError("Monthly Charges must be a valid non-negative number.");
      return;
    }

    if (
      !Number.isFinite(form.TotalCharges) ||
      form.TotalCharges < 0
    ) {
      setError("Total Charges must be a valid non-negative number.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await api.post<PredictionResult>("/predict", form);
      const data = response.data;

      if (
        !data ||
        !Number.isFinite(data.churn_percentage) ||
        !["High", "Medium", "Low"].includes(data.risk_level) ||
        !Array.isArray(data.recommendations)
      ) {
        throw new Error("Invalid prediction response from server.");
      }

      setResult(data);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;

        setError(
          typeof detail === "string"
            ? detail
            : err.response
              ? "The server could not process this prediction. Check the customer inputs."
              : "Unable to connect to ChurnGuard API. Check whether the backend server is running."
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred while generating the prediction.");
      }
    } finally {
      setLoading(false);
    }
  };

  const renderSelect = (
    label: string,
    field: keyof CustomerForm,
    options: string[]
  ) => (
    <div className="form-group">
      <label htmlFor={field}>{label}</label>
      <select
        id={field}
        value={String(form[field])}
        onChange={(e) => updateField(field, e.target.value)}
        disabled={loading}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );

  const renderNumber = (
    label: string,
    field: "SeniorCitizen" | "tenure" | "MonthlyCharges" | "TotalCharges",
    min: number,
    max?: number
  ) => (
    <div className="form-group">
      <label htmlFor={field}>{label}</label>
      <input
        id={field}
        type="number"
        min={min}
        max={max}
        step={
          field === "MonthlyCharges" || field === "TotalCharges"
            ? "0.01"
            : "1"
        }
        value={form[field]}
        onChange={(e) => {
          const value = e.target.value;
          updateField(field, value === "" ? NaN : Number(value));
        }}
        required
        disabled={loading}
      />
    </div>
  );

  return (
    <main className="dashboard prediction-page">
      <header className="dashboard-header">
        <div>
          <h1>Customer Churn Prediction</h1>
          <p>
            Enter customer details to predict churn probability
            and generate retention recommendations.
          </p>
        </div>
      </header>

      <div className="prediction-layout">
        <form className="prediction-form" onSubmit={handleSubmit}>
          <div className="form-heading">
            <BrainCircuit size={23} />
            <div>
              <h2>Customer Information</h2>
              <p>Enter the customer's account and service details.</p>
            </div>
          </div>

          <h3 className="form-section-title">Personal Information</h3>

          <div className="form-grid">
            {renderSelect("Gender", "gender", ["Female", "Male"])}
            {renderNumber(
              "Senior Citizen (0 = No, 1 = Yes)",
              "SeniorCitizen",
              0,
              1
            )}
            {renderSelect("Partner", "Partner", ["Yes", "No"])}
            {renderSelect("Dependents", "Dependents", ["Yes", "No"])}
          </div>

          <h3 className="form-section-title">Account Information</h3>

          <div className="form-grid">
            {renderNumber("Tenure (months)", "tenure", 0, 100)}
            {renderSelect("Contract", "Contract", [
              "Month-to-month",
              "One year",
              "Two year",
            ])}
            {renderSelect("Paperless Billing", "PaperlessBilling", [
              "Yes",
              "No",
            ])}
            {renderSelect("Payment Method", "PaymentMethod", [
              "Electronic check",
              "Mailed check",
              "Bank transfer (automatic)",
              "Credit card (automatic)",
            ])}
          </div>

          <h3 className="form-section-title">Service Information</h3>

          <div className="form-grid">
            {renderSelect("Phone Service", "PhoneService", ["Yes", "No"])}
            {renderSelect("Multiple Lines", "MultipleLines", [
              "Yes",
              "No",
              "No phone service",
            ])}
            {renderSelect("Internet Service", "InternetService", [
              "DSL",
              "Fiber optic",
              "No",
            ])}
            {renderSelect("Online Security", "OnlineSecurity", [
              "Yes",
              "No",
              "No internet service",
            ])}
            {renderSelect("Online Backup", "OnlineBackup", [
              "Yes",
              "No",
              "No internet service",
            ])}
            {renderSelect("Device Protection", "DeviceProtection", [
              "Yes",
              "No",
              "No internet service",
            ])}
            {renderSelect("Tech Support", "TechSupport", [
              "Yes",
              "No",
              "No internet service",
            ])}
            {renderSelect("Streaming TV", "StreamingTV", [
              "Yes",
              "No",
              "No internet service",
            ])}
            {renderSelect("Streaming Movies", "StreamingMovies", [
              "Yes",
              "No",
              "No internet service",
            ])}
          </div>

          <h3 className="form-section-title">Billing Information</h3>

          <div className="form-grid">
            {renderNumber("Monthly Charges", "MonthlyCharges", 0)}
            {renderNumber("Total Charges", "TotalCharges", 0)}
          </div>

          {error && (
            <div className="prediction-error">
              <ServerCrash size={18} />
              <span>{error}</span>
              <button
                type="submit"
                className="prediction-retry"
                disabled={loading}
              >
              <RefreshCw size={15} />
              Retry
              </button>
            </div>
          )}

          <button
            id="predict-submit"
            className="predict-button"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="spin" size={19} />
                Analyzing Customer...
              </>
            ) : (
              <>
                <BrainCircuit size={19} />
                Predict Customer Churn
              </>
            )}
          </button>
        </form>

        <section className="prediction-result">
          <h2>Prediction Results</h2>
          <p className="chart-subtitle">
            Your model's prediction will appear here.
          </p>

          {!result && !loading && (
            <div className="empty-result">
              <BrainCircuit size={48} />
              <h3>Awaiting Customer Data</h3>
              <p>
                Fill in the customer information and click
                Predict Customer Churn.
              </p>
            </div>
          )}

          {loading && (
            <div className="prediction-loading">
              <Loader2 className="spin" size={42} />
              <h3>Analyzing Customer</h3>
              <p>
                Your customer data is being processed by the churn
                prediction model.
              </p>
              <div className="prediction-progress">
                <div />
              </div>
            </div>
          )}

          {result && !loading && (
            <div className="result-content">
              <div className="result-score">
                <span>Churn Probability</span>
                <h1>{result.churn_percentage.toFixed(2)}%</h1>
              </div>

              <div className={`risk-result ${result.risk_level.toLowerCase()}`}>
                <AlertTriangle size={22} />
                <div>
                  <strong>{result.risk_level} Risk</strong>
                  <p>Retention Priority: {result.retention_priority}</p>
                </div>
              </div>

              <h3>Retention Recommendations</h3>

              <div className="recommendation-list">
                {result.recommendations.map(
                  (recommendation, index) => (
                    <div className="recommendation-item" key={index}>
                      <CheckCircle size={18} />
                      <span>{recommendation}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
};

export default CustomerPrediction;
