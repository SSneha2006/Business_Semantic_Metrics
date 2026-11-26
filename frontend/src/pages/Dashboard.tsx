
import {
  Database,
  Calculator,
  GitCompare,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";

import StatCard from "../components/StatCard";

const revenueData = [
  { month: "Jan", revenue: 42000, expenses: 25000 },
  { month: "Feb", revenue: 48000, expenses: 28000 },
  { month: "Mar", revenue: 45000, expenses: 26000 },
  { month: "Apr", revenue: 58000, expenses: 31000 },
  { month: "May", revenue: 62000, expenses: 35000 },
  { month: "Jun", revenue: 70000, expenses: 39000 },
];

const metricData = [
  { name: "Sales", metrics: 12 },
  { name: "Finance", metrics: 9 },
  { name: "Marketing", metrics: 7 },
  { name: "Operations", metrics: 5 },
];

export default function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="welcome-section">
        <div>
          <h1>Dashboard Overview</h1>
          <p>
            Welcome back! Here's what's happening with your business metrics.
          </p>
        </div>

        <button className="primary-button">
          <Activity size={17} />
          View Reports
        </button>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Datasets"
          value="24"
          change="+12% from last month"
          icon={Database}
        />

        <StatCard
          title="Active Metrics"
          value="48"
          change="+8% from last month"
          icon={Calculator}
        />

        <StatCard
          title="Metric Conflicts"
          value="06"
          change="2 fewer than last month"
          icon={GitCompare}
        />

        <StatCard
          title="Data Accuracy"
          value="98.5%"
          change="+2.4% from last month"
          icon={TrendingUp}
        />
      </div>

      <div className="charts-grid">
        <div className="chart-card revenue-card">
          <div className="chart-heading">
            <div>
              <h3>Revenue Overview</h3>
              <p>Monthly revenue and expenses</p>
            </div>
            <span className="chart-period">Last 6 months</span>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData}>
                <defs>
                  <linearGradient id="revenueColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6366f1"
                  fill="url(#revenueColor)"
                  strokeWidth={3}
                />
                <Area
                  type="monotone"
                  dataKey="expenses"
                  stroke="#f59e0b"
                  fill="none"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-heading">
            <div>
              <h3>Department Metrics</h3>
              <p>Metrics by department</p>
            </div>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metricData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar
                  dataKey="metrics"
                  fill="#6366f1"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bottom-grid">
        <div className="activity-card">
          <h3>Recent Activity</h3>

          <div className="activity-item">
            <div className="activity-icon purple">
              <Database size={18} />
            </div>
            <div>
              <strong>New dataset uploaded</strong>
              <p>Sales_Q2_2026.csv</p>
            </div>
            <span>10 min ago</span>
          </div>

          <div className="activity-item">
            <div className="activity-icon green">
              <Calculator size={18} />
            </div>
            <div>
              <strong>Metric definition updated</strong>
              <p>Net Revenue</p>
            </div>
            <span>1 hour ago</span>
          </div>

          <div className="activity-item">
            <div className="activity-icon orange">
              <GitCompare size={18} />
            </div>
            <div>
              <strong>Metric conflict detected</strong>
              <p>Revenue definition mismatch</p>
            </div>
            <span>3 hours ago</span>
          </div>
        </div>

        <div className="consistency-card">
          <h3>Metric Consistency</h3>
          <div className="consistency-score">94%</div>
          <p>Overall consistency score</p>
          <div className="progress-track">
            <div className="progress-value" />
          </div>
          <div className="consistency-footer">
            <span><ArrowUpRight size={15} /> 4.2% improvement</span>
            <span>Across departments</span>
          </div>
        </div>
      </div>
    </div>
  );
}
