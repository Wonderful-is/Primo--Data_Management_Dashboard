// Base URL of the FastAPI backend deployed on Render.
// Set NEXT_PUBLIC_API_URL in Vercel's project environment variables, e.g.
//   NEXT_PUBLIC_API_URL=https://primo-audit-dashboard-api.onrender.com
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getJSON(path) {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Request to ${path} failed with status ${res.status}`);
  }
  return res.json();
}

export function toQuery(params) {
  const usp = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    if (Array.isArray(value)) {
      if (value.length > 0) usp.set(key, value.join(","));
    } else {
      usp.set(key, value);
    }
  });
  const qs = usp.toString();
  return qs ? `?${qs}` : "";
}

export const api = {
  health: () => getJSON("/api/health"),

  overviewFilters: () => getJSON("/api/overview/filters"),
  overviewData: (params) => getJSON(`/api/overview/data${toQuery(params)}`),

  reviewFilters: () => getJSON("/api/review/filters"),
  reviewData: (params) => getJSON(`/api/review/data${toQuery(params)}`),

  dailyMissingFilters: () => getJSON("/api/daily-missing/filters"),
  dailyMissingData: (params) => getJSON(`/api/daily-missing/data${toQuery(params)}`),
};
