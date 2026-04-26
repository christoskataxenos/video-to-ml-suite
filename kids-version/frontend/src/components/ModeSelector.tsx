/**
 * ModeSelector — Κάρτες επιλογής mode (sticker/catch, mascot/icon/audio κλπ).
 * Γενικό component που χρησιμοποιείται σε πολλά σημεία του Parent Dashboard.
 */

interface ModeOption {
  value: string;
  label: string;
  description: string;
  icon: string;
}

interface ModeSelectorProps {
  options: ModeOption[];
  selected: string;
  onChange: (value: string) => void;
  label: string;
}

export default function ModeSelector({ options, selected, onChange, label }: ModeSelectorProps) {
  return (
    <div className="form-group">
      <span className="form-label">{label}</span>
      <div className="options-grid">
        {options.map((option) => (
          <div
            key={option.value}
            className={`card card-selectable ${selected === option.value ? "selected" : ""}`}
            onClick={() => onChange(option.value)}
            role="radio"
            aria-checked={selected === option.value}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onChange(option.value);
              }
            }}
          >
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>{option.icon}</div>
            <div style={{ fontWeight: 600, fontSize: "1.05rem", marginBottom: "4px" }}>
              {option.label}
            </div>
            <div style={{ fontSize: "0.85rem", opacity: 0.7, lineHeight: 1.4 }}>
              {option.description}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
