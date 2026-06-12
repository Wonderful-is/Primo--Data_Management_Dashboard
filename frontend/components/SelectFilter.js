export default function SelectFilter({ label, options, value, onChange }) {
  return (
    <div className="mb-4">
      <div className="text-xs font-semibold uppercase text-gray-500 mb-1">{label}</div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-gray-300 rounded px-2 py-1 text-sm bg-white"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
}
