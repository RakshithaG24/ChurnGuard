
import { useCallback, useEffect, useState } from "react";
import {
  Users,
  AlertTriangle,
  ShieldCheck,
  Activity,
  RefreshCw,
  ServerCrash,
} from "lucide-react";

import StatCard from "../components/StatCard";
import RiskChart from "../components/RiskChart";
import { getAnalytics } from "../services/api";

interface Analytics {
  total_customers: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  average_churn_probability: number;
  high_risk_percentage: number;
}

const Dashboard = () => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getAnalytics();

      if (
        !data ||
        !Number.isFinite(data.total_customers) ||
        !Number.isFinite(data.high_risk) ||
        !Number.isFinite(data.medium_risk) ||
        !Number.isFinite(data.low_risk)
      ) {
        throw new Error("Invalid analytics response");
      }

      setAnalytics(data);
    } catch {
      setAnalytics(null);
      setError(
        "Unable to load dashboard data. Please check whether the ChurnGuard API is running."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  if (loading) {
    return (
      <main className="dashboard">
        <div className="dashboard-header">
          <div>
            <h1>Dashboard Overview</h1>
            <p>Loading your customer analytics...</p>
          </div>
        </div>

        <section className="stats-grid">
          {[1, 2, 3, 4].map((item) => (
            <div className="loading-card" key={item}>
              <div className="skeleton skeleton-label" />
              <div className="skeleton skeleton-value" />
              <div className="skeleton skeleton-description" />
            </div>
          ))}
        </section>

        <div className="dashboard-grid">
          <div className="loading-card chart-loading">
            <div className="skeleton skeleton-label" />
            <div className="skeleton skeleton-chart" />
          </div>

          <div className="loading-card chart-loading">
            <div className="skeleton skeleton-label" />
            <div className="skeleton skeleton-description" />
            <div className="skeleton skeleton-description" />
            <div className="skeleton skeleton-description" />
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="dashboard">
        <div className="api-error-card">
          <ServerCrash size={42} />
          <h2>Dashboard unavailable</h2>
          <p>{error}</p>

          <button
            className="retry-button"
            onClick={loadAnalytics}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Retry connection
          </button>
        </div>
      </main>
    );
  }

  if (!analytics || analytics.total_customers === 0) {
    return (
      <main className="dashboard">
        <div className="empty-dashboard">
          <Users size={42} />
          <h2>No customer data available</h2>
          <p>There are currently no customers to display.</p>

          <button className="retry-button" onClick={loadAnalytics}>
            <RefreshCw size={17} />
            Refresh data
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Dashboard Overview</h1>
          <p>Monitor customer churn and retention performance.</p>
        </div>

        <div className="status-indicator">
          <span className="status-dot"></span>
          System Active
        </div>
      </header>

      <section className="stats-grid">
        <StatCard
          title="Total Customers"
          value={analytics.total_customers.toLocaleString()}
          description="Customers analyzed"
          icon={Users}
          color="blue"
        />

        <StatCard
          title="High Risk Customers"
          value={analytics.high_risk.toString()}
          description={`${analytics.high_risk_percentage}% of customers`}
          icon={AlertTriangle}
          color="red"
        />

        <StatCard
          title="Average Churn Probability"
          value={`${(analytics.average_churn_probability * 100).toFixed(2)}%`}
          description="Average predicted likelihood"
          icon={Activity}
          color="orange"
        />

        <StatCard
          title="Low Risk Customers"
          value={analytics.low_risk.toString()}
          description="Customers with lower predicted risk"
          icon={ShieldCheck}
          color="green"
        />
      </section>

      <section className="dashboard-grid">
        <RiskChart
          high={analytics.high_risk}
          medium={analytics.medium_risk}
          low={analytics.low_risk}
        />

        <div className="insights-card">
          <h3>Retention Insights</h3>
          <p className="chart-subtitle">
            Current customer risk overview
          </p>

          <div className="insight-row">
            <span className="risk-dot red-dot"></span>
            <span>High Risk</span>
            <strong>{analytics.high_risk}</strong>
          </div>

          <div className="insight-row">
            <span className="risk-dot orange-dot"></span>
            <span>Medium Risk</span>
            <strong>{analytics.medium_risk}</strong>
          </div>

          <div className="insight-row">
            <span className="risk-dot green-dot"></span>
            <span>Low Risk</span>
            <strong>{analytics.low_risk}</strong>
          </div>

          <div className="insight-message">
            Prioritize retention follow-ups for high-risk customers.
          </div>
        </div>
      </section>
    </main>
  );
};

export default Dashboard;
