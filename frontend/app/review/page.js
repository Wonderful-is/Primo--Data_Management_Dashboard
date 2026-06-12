"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";
import KpiCard from "../../components/KpiCard";
import CheckboxFilter from "../../components/CheckboxFilter";
import SelectFilter from "../../components/SelectFilter";
import DataTable from "../../components/DataTable";

export default function ReviewPage() {
  const [filters, setFilters] = useState(null);
  const [sites, setSites] = useState([]);
  const [arm, setArm] = useState("All");
  const [ptype, setPtype] = useState("All");
  const [form, setForm] = useState(null);
  const [event, setEvent] = useState(null);
  const [completion, setCompletion] = useState("Missing");
  const [babyLink, setBabyLink] = useState("All");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .reviewFilters()
      .then((f) => {
        setFilters(f);
        setSites(f.site_options);
        const allowedForms = f.arm_allowed_forms["All"];
        setForm(allowedForms[0]);
        const allowedEvents = f.form_event_map[allowedForms[0]] || [];
        setEvent(allowedEvents[0] || null);
      })
      .catch((e) => setError(e.message));
  }, []);

  // form options depend on arm
  const formOptions = useMemo(() => {
    if (!filters) return [];
    return filters.arm_allowed_forms[arm] || filters.arm_allowed_forms["All"];
  }, [filters, arm]);

  // event options depend on form
  const eventOptions = useMemo(() => {
    if (!filters || !form) return [];
    return filters.form_event_map[form] || [];
  }, [filters, form]);

  // keep form valid when arm changes
  useEffect(() => {
    if (!filters) return;
    if (!formOptions.includes(form)) {
      setForm(formOptions[0]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [arm, filters]);

  // keep event valid when form changes
  useEffect(() => {
    if (!filters) return;
    if (!eventOptions.includes(event)) {
      setEvent(eventOptions[0] || null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form, filters]);

  useEffect(() => {
    if (!filters || !form || !event) return;
    setLoading(true);
    api
      .reviewData({ sites, arm, ptype, form, event, completion, baby_link: babyLink })
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, sites, arm, ptype, form, event, completion, babyLink]);

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
    <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <aside className="lg:col-span-1 bg-white rounded-xl shadow-sm p-4">
        <h2 className="text-sm font-bold text-primo-900 mb-3">FILTERS</h2>
        <CheckboxFilter label="Site" options={filters.site_options} value={sites} onChange={setSites} />
        <SelectFilter label="Study Arm" options={filters.arm_options} value={arm} onChange={setArm} />
        <SelectFilter label="Participant Type" options={filters.ptype_options} value={ptype} onChange={setPtype} />

        <SelectFilter
          label="Form to Review"
          options={formOptions}
          value={form || ""}
          onChange={setForm}
        />

        <SelectFilter
          label="Visit / Event"
          options={eventOptions}
          value={event || ""}
          onChange={setEvent}
        />

        <SelectFilter
          label="Completion Status"
          options={["All", "Completed", "Missing"]}
          value={completion}
          onChange={setCompletion}
        />

        <SelectFilter
          label="Mother-Baby Linkage Status"
          options={filters.baby_link_options}
          value={babyLink}
          onChange={setBabyLink}
        />
      </aside>

      <div className="lg:col-span-4 flex flex-col gap-4">
        <div>
          <h1 className="text-xl font-bold text-primo-900">PRIMO Participant Form Completion Review</h1>
          <p className="text-sm text-gray-500">
            Identify eligible participants who completed or are missing selected forms by visit/event.
          </p>
        </div>

        {loading && <div className="text-sm text-gray-400">Refreshing data&hellip;</div>}

        {kpis && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <KpiCard title="Eligible Participants" value={kpis.total} />
            <KpiCard title="Completed" value={kpis.completed} />
            <KpiCard title="Missing" value={kpis.missing} />
            <KpiCard title="Completion %" value={`${kpis.completion_pct}%`} />
          </div>
        )}

        {result?.eligibility_note && (
          <div className="bg-blue-50 border border-blue-200 text-blue-800 text-sm rounded p-3">
            {result.eligibility_note}
          </div>
        )}

        <div className="chart-card">
          <div className="chart-title">Participant Review List</div>
          {result && (
            <DataTable
              columns={result.columns}
              rows={result.rows}
              maxHeight="600px"
              statusColumn="form_status"
            />
          )}
        </div>
      </div>
    </div>
  );
}
