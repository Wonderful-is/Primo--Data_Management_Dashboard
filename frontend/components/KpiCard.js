export default function KpiCard({ title, value }) {
  return (
    <div className="kpi-card">
      <div className="kpi-title">{title}</div>
      <div className="kpi-value">
        {typeof value === "number" ? value.toLocaleString() : value}
      </div>
    </div>
  );
}
