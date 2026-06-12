"use client";

import { useEffect, useState } from "react";
import { api } from "../lib/api";
import KpiCard from "../components/KpiCard";
import CheckboxFilter from "../components/CheckboxFilter";
import SelectFilter from "../components/SelectFilter";
import DataTable from "../components/DataTable";
import { SimplePie, SimpleBar, SimpleLine } from "../components/Charts";

export default function OverviewPage() {
  const [filters, setFilters] = useState(null);
  const [sites, setSites] = useState([]);
  const [forms, setForms] = useState([]);
  const [ptype, setPtype] = useState("All");
  const [statuses, setStatuses] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load filter options once.
  useEffect(() => {
    api
      .overviewFilters()
      .then((f) => {
        setFilters(f);
        setSites(f.sites);
        setForms(f.forms);
        setStatuses(f.statuses);
      })
      .catch((e) => setError(e.message));
  }, []);

  // Reload data whenever filters change.
  useEffect(() => {
    if (!filters) return;
    setLoading(true);
    api
      .overviewData({ sites, forms, ptype, status: statuses })
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, sites, forms, ptype, statuses]);

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 border border-red-200 rounded p-4 text-sm">
        Could not reach the backend API ({error}). Make sure
        <code className="mx-1 bg-red-100 px-1 rounded">NEXT_PUBLIC_API_URL</code>
        is set and your Render service is running.
      </div>
    );
  }

  if (!filters) {
    return <div className="text-sm text-gray-500">Loading filters&hellip;</div>;
  }

  const kpis = result?.kpis;
  const charts = result?.charts;
  const queryLog = result?.query_log;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
      {/* Sidebar */}
      <aside className="lg:col-span-1 bg-white rounded-xl shadow-sm p-4">
        <h2 className="text-sm font-bold text-primo-900 mb-3">FILTERS</h2>
        <CheckboxFilter label="Site" options={filters.sites} value={sites} onChange={setSites} />
        <CheckboxFilter label="Form" options={filters.forms} value={forms} onChange={setForms} />
        <SelectFilter
          label="Participant Type"
          options={["All", ...filters.participant_types]}
          value={ptype}
          onChange={setPtype}
        />
        <CheckboxFilter
          label="Query Status"
          options={filters.statuses}
          value={statuses}
          onChange={setStatuses}
        />
      </aside>

      {/* Main content */}
      <div className="lg:col-span-4 flex flex-col gap-4">
        <div>
          <h1 className="text-xl font-bold text-primo-900">
            PRIMO Clinical Data Management Quality Dashboard
          </h1>
          <p className="text-sm text-gray-500">
            Real-time overview of data quality, completeness and query status
          </p>
        </div>

        {loading && <div className="text-sm text-gray-400">Refreshing data&hellip;</div>}

        {kpis && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            <KpiCard title="Total Records" value={kpis.total_records} />
            <KpiCard title="Participants" value={kpis.participants} />
            <KpiCard title="Mothers" value={kpis.mothers} />
            <KpiCard title="Babies" value={kpis.babies} />
            <KpiCard title="Sites" value={kpis.sites} />
            <KpiCard title="Open Queries" value={kpis.open_queries} />
          </div>
        )}

        {charts && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <SimplePie title="Records by Participant Type" data={charts.participant_type} />
              <SimpleBar
                title="Participants by Site"
                data={charts.by_site}
                dataKey="Participants"
                layout="vertical"
              />
              <SimpleBar
                title="Form Inventory"
                data={charts.by_form}
                dataKey="Records"
                layout="vertical"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <SimpleLine title="Maternal Daily Coverage" data={charts.daily_coverage} dataKey="Participants" />
              <SimpleLine title="Prenatal Follow-up Coverage" data={charts.prenatal_coverage} dataKey="Participants" />
              <SimpleLine title="Neonatal Follow-up" data={charts.neonatal_coverage} dataKey="Babies" />
              <SimpleLine title="Neonatal Clinical Pathogen" data={charts.neonatal_cp_coverage} dataKey="Babies" />
            </div>
          </>
        )}

        {charts && queryLog && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-1">
              <SimpleBar title="Query Status" data={charts.query_status} dataKey="Count" />
            </div>
            <div className="lg:col-span-2 chart-card">
              <div className="chart-title">Participant ID Query Log</div>
              <DataTable columns={queryLog.columns} rows={queryLog.rows} maxHeight="320px" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
