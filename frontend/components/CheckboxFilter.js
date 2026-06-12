export default function CheckboxFilter({ label, options, value, onChange }) {
  const toggle = (opt) => {
    if (value.includes(opt)) {
      onChange(value.filter((v) => v !== opt));
    } else {
      onChange([...value, opt]);
    }
  };

  return (
    <div className="mb-4">
      <div className="text-xs font-semibold uppercase text-gray-500 mb-1">{label}</div>
      <div className="flex flex-col gap-1 max-h-40 overflow-y-auto pr-1">
        {options.map((opt) => (
          <label key={opt} className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={value.includes(opt)}
              onChange={() => toggle(opt)}
              className="accent-primo-700"
            />
            {opt}
          </label>
        ))}
      </div>
    </div>
  );
}
