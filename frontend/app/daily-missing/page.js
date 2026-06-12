"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import KpiCard from "../../components/KpiCard";
import CheckboxFilter from "../../components/CheckboxFilter";
import SelectFilter from "../../components/SelectFilter";
import DataTable from "../../components/DataTable";

export default function DailyMissingPage() {
  const [filters, setFilters] = useState(null);
  const [sites, setSites] = useState([]);
  const [includeVisits, setIncludeVisits] = useState([]);
  const [excludeVisits, setExcludeVisits] = useState([]);
  const [deliveryFilter, setDeliveryFilter] = useState("All");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .dailyMissingFilters()
      .then((f) => {
        setFilters(f);
        setSites(f.site_options);
        const defaultInclude = ["Day 8", "Day 14", "Day 21", "Day 60", "Day 180"].filter((v) =>
          f.visit_labels.includes(v)
        );
        setIncludeVisits(defaultInclude.length ? defaultInclude : f.visit_labels);
      })
      .catch((e) => setError(e.message));
  }, []);

  const excludeOptions = useMemo(() => {
    if (!filters) return [];
    return filters.visit_labels.filter((v) => !includeVisits.includes(v));
  }, [filters, includeVisits]);

  useEffect(() => {
    setExcludeVisits((prev) => prev.filter((v) => excludeOptions.includes(v)));
  }, [excludeOptions]);

  useEffect(() => {
    if (!filters) return;
    setLoading(true);
    api
      .dailyMissingData({
        sites,
        include_visits: includeVisits,
        exclude_visits: excludeVisits,
        delivery_filter: deliveryFilter,
      })
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, sites, includeVisits, excludeVisits, deliveryFilter]);

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 border border-red-200 rounded p-4 text-sm">
        Could not reach the backend API ({error}).
      </div>
    );
  }

  if (!filters) {
    return <div className="text-sm text-gray-500">Loading filters&hellip;</div>;
  }

  const kpis = result?.kpis;

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-xl font-bold text-primo-900">
          PRIMO Date-Aware Daily Form Missing Visit Review
        </h1>
        <p className="text-sm text-gray-500">
          Identifies mothers who are truly missing daily forms by checking whether each visit was
          expected based on enrollment date and delivery / baby date of birth.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white rounded-xl shadow-sm p-4">
        <CheckboxFilter label="Site" options={filters.site_options} value={sites} onChange={setSites} />
        <CheckboxFilter
          label="Participants missing ALL these visits"
          options={filters.visit_labels}
          value={includeVisits}
          onChange={setIncludeVisits}
        />
        <CheckboxFilter
          label="Exclude participants missing ALL these visits"
          options={excludeOptions}
          value={excludeVisits}
          onChange={setExcludeVisits}
        />
        <SelectFilter
          label="Postpartum / baby filter"
          options={filters.delivery_filter_options}
          value={deliveryFilter}
          onChange={setDeliveryFilter}
        />
      </div>

      {loading && <div className="text-sm text-gray-400">Refreshing data&hellip;</div>}

      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard title="Eligible Mothers" value={kpis.eligible} />
          <KpiCard title="Matched Participants" value={kpis.matched} />
          <KpiCard title="Included Missing Pattern" value={kpis.include_pattern} />
          <KpiCard title="Excluded Missing Pattern" value={kpis.exclude_pattern} />
        </div>
      )}

      {result?.note && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 text-sm rounded p-3">
          {result.note}
        </div>
      )}

      <div className="chart-card">
        <div className="chart-title">Missing Visits Summary</div>
        {result && (
          <DataTable columns={result.summary_table.columns} rows={result.summary_table.rows} maxHeight="260px" />
        )}
      </div>

      <div className="chart-card">
        <div className="chart-title">Participant Review List</div>
        {result && (
          <DataTable
            columns={result.missing_table.columns}
            rows={result.missing_table.rows}
            maxHeight="600px"
            statusSuffix="_status"
          />
        )}
      </div>
    </div>
  );
}
