import "./TouchOptions.css";

export default function TouchOptions({
  label,
  options,
  values,
  selected,
  onSelect,
}) {
  return (
    <div className="touch-options">
      <p className="touch-options__label">
        {label}
      </p>

      <div className="touch-options__grid">
        {options.map((option, index) => {
          const value = values[index];

          const isSelected = selected === value;

          return (
            <button
              key={value}
              type="button"
              className={`touch-options__button ${
                isSelected
                  ? "touch-options__button--selected"
                  : ""
              }`}
              onClick={() => onSelect(value)}
              aria-pressed={isSelected}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}