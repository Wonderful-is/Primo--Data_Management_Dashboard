export default function DataTable({ columns, rows, maxHeight = "400px", statusColumn, statusSuffix }) {
  if (!columns || columns.length === 0) {
    return <div className="text-sm text-gray-400 italic">No data to display.</div>;
  }

  return (
    <div className="overflow-auto border border-gray-100 rounded" style={{ maxHeight }}>
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((c) => {
                const val = row[c];
                let cls = "";
                if (statusColumn && c === statusColumn) {
                  if (val === "Missing") cls = "status-missing";
                  if (val === "Completed") cls = "status-completed";
                }
                if (statusSuffix && c.endsWith(statusSuffix)) {
                  if (val === "Missing") cls = "status-missing";
                  if (val === "Completed") cls = "status-completed";
                }
                return (
                  <td key={c} className={cls}>
                    {val === null || val === undefined || val === "" ? "" : String(val)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
