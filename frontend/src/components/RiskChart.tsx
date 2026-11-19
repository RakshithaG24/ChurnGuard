
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface RiskChartProps {
  high: number;
  medium: number;
  low: number;
}

const RiskChart = ({ high, medium, low }: RiskChartProps) => {
  const data = [
    { name: "High Risk", value: high, color: "#ef4444" },
    { name: "Medium Risk", value: medium, color: "#f59e0b" },
    { name: "Low Risk", value: low, color: "#10b981" },
  ];

  return (
    <div className="chart-card">
      <h3>Customer Risk Distribution</h3>
      <p className="chart-subtitle">
        Breakdown of predicted customer churn risk
      </p>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={105}
              paddingAngle={4}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend verticalAlign="bottom" />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RiskChart;
