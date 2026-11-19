
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { Activity, TrendingUp, Users, BrainCircuit } from "lucide-react";
import api from "../services/api";

interface ChurnGroup {
  category: string;
  customers: number;
  churned?: number;
  churn_rate?: number;
}

interface AnalyticsData {
  contract_churn: ChurnGroup[];
  internet_churn: ChurnGroup[];
  tenure_churn: ChurnGroup[];
  payment_churn: ChurnGroup[];
  risk_distribution: ChurnGroup[];
}

const COLORS = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6"];

const Analytics = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [features, setFeatures] = useState<ChurnGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const [insightsResponse, featureResponse] = await Promise.all([
          api.get("/analytics/insights"),
          api.get("/analytics/feature-importance"),
        ]);

        setData(insightsResponse.data);
        setFeatures(featureResponse.data.features);
      } catch {
        setError(
          "Unable to load analytics. Check the backend and analytics endpoints."
        );
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return <main className="dashboard">Loading advanced analytics...</main>;
  }

  if (error || !data) {
    return <main className="dashboard analytics-error">{error}</main>;
  }

  const totalCustomers = data.risk_distribution.reduce(
    (sum, item) => sum + item.customers,
    0
  );

  const averageChurnRate = (
    [
      ...data.contract_churn,
    ].reduce((sum, item) => sum + (item.churn_rate || 0) * item.customers, 0) /
    Math.max(
      1,
      data.contract_churn.reduce((sum, item) => sum + item.customers, 0)
    )
  ).toFixed(2);

  const riskColors: Record<string, string> = {
    High: "#ef4444",
    Medium: "#f59e0b",
    Low: "#10b981",
  };

  return (
    <main className="dashboard analytics-page">
      <header className="dashboard-header">
        <div>
          <h1>Advanced Analytics</h1>
          <p>Explore churn patterns, customer behavior and model insights.</p>
        </div>
        <div className="status-indicator">
          <span className="status-dot" />
          Analytics Updated
        </div>
      </header>

      <section className="stats-grid analytics-stats">
        <div className="stat-card">
          <div className="stat-top">
            <span>Analyzed Customers</span>
            <Users size={21} />
          </div>
          <h2>{totalCustomers.toLocaleString()}</h2>
          <p>Test dataset</p>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span>Contract-weighted Churn Rate</span>
            <TrendingUp size={21} />
          </div>
          <h2>{averageChurnRate}%</h2>
          <p>Actual churn labels, test dataset</p>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span>High Risk Customers</span>
            <Activity size={21} />
          </div>
          <h2>
            {data.risk_distribution.find((item) => item.category === "High")
              ?.customers ?? 0}
          </h2>
          <p>Predicted risk category</p>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span>SHAP Features</span>
            <BrainCircuit size={21} />
          </div>
          <h2>{features.length}</h2>
          <p>Global feature importance entries</p>
        </div>
      </section>

      <section className="analytics-grid">
        <div className="chart-card">
          <h3>Churn Rate by Contract</h3>
          <p className="chart-subtitle">Actual churn percentage by contract type</p>
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.contract_churn}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis unit="%" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="churn_rate" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Churn Rate by Internet Service</h3>
          <p className="chart-subtitle">Actual churn percentage by service type</p>
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.internet_churn}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis unit="%" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="churn_rate" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Churn Rate by Tenure</h3>
          <p className="chart-subtitle">How churn varies with customer tenure</p>
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.tenure_churn}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis unit="%" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="churn_rate" fill="#10b981" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Churn Rate by Payment Method</h3>
          <p className="chart-subtitle">Actual churn percentage by payment type</p>
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.payment_churn}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" interval={0} angle={-15} textAnchor="end" height={65} />
                <YAxis unit="%" />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="churn_rate" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Predicted Customer Risk Distribution</h3>
          <p className="chart-subtitle">Model-generated risk categories</p>
          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.risk_distribution}
                  dataKey="customers"
                  nameKey="category"
                  innerRadius={65}
                  outerRadius={105}
                  paddingAngle={4}
                >
                  {data.risk_distribution.map((item) => (
                    <Cell
                      key={item.category}
                      fill={riskColors[item.category] || "#64748b"}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <h3>Top SHAP Feature Importance</h3>
          <p className="chart-subtitle">
            Mean absolute SHAP values from your trained model
          </p>

          <div className="feature-list">
            {features.slice(0, 10).map((feature) => (
              <div className="feature-item" key={feature.category}>
                <div className="feature-label">
                  <span>{feature.category.replace(/^(num__|cat__)/, "")}</span>
                  <strong>{feature.customers.toFixed(4)}</strong>
                </div>
                <div className="feature-track">
                  <div
                    className="feature-fill"
                    style={{
                      width: `${
                        (feature.customers /
                          Math.max(...features.map((item) => item.customers), 0.0001)) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
};

export default Analytics;
