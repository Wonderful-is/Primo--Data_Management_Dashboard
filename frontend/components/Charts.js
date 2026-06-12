"use client";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
} from "recharts";

const COLORS = ["#1F4E79", "#3E7CB1", "#81A4CD", "#D4E4F7", "#0B2545", "#A7C7E7"];

export function ChartCard({ title, children, height = 280 }) {
  return (
    <div className="chart-card">
      <div className="chart-title">{title}</div>
      <ResponsiveContainer width="100%" height={height}>
        {children}
      </ResponsiveContainer>
    </div>
  );
}

export function SimplePie({ title, data }) {
  if (!data || data.length === 0) {
    return (
      <ChartCard title={title}>
        <div />
      </ChartCard>
    );
  }
  return (
    <ChartCard title={title}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={50} outerRadius={85} label>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ChartCard>
  );
}

export function SimpleBar({ title, data, dataKey, layout = "horizontal" }) {
  return (
    <ChartCard title={title}>
      <BarChart data={data} layout={layout}>
        <CartesianGrid strokeDasharray="3 3" />
        {layout === "vertical" ? (
          <>
            <XAxis type="number" />
            <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11 }} />
          </>
        ) : (
          <>
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
          </>
        )}
        <Tooltip />
        <Bar dataKey={dataKey} fill="#1F4E79" />
      </BarChart>
    </ChartCard>
  );
}

export function SimpleLine({ title, data, dataKey }) {
  return (
    <ChartCard title={title} height={240}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={dataKey} stroke="#1F4E79" strokeWidth={2} dot />
      </LineChart>
    </ChartCard>
  );
}
