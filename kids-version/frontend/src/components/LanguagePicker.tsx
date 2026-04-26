/**
 * LanguagePicker — Επιλογέας γλώσσας με σημαίες.
 * Χρησιμοποιείται τόσο στο Parent Dashboard όσο και στο Kids UI.
 */

interface LanguagePickerProps {
  selected: "en" | "el" | "de";
  onChange: (lang: "en" | "el" | "de") => void;
}

const FLAGS: Record<string, { emoji: string; label: string }> = {
  en: { emoji: "🇬🇧", label: "English" },
  el: { emoji: "🇬🇷", label: "Ελληνικά" },
  de: { emoji: "🇩🇪", label: "Deutsch" },
};

export default function LanguagePicker({ selected, onChange }: LanguagePickerProps) {
  return (
    <div className="language-picker" role="radiogroup" aria-label="Language selection">
      {Object.entries(FLAGS).map(([code, { emoji, label }]) => (
        <button
          key={code}
          className={`language-flag ${selected === code ? "active" : ""}`}
          onClick={() => onChange(code as "en" | "el" | "de")}
          aria-label={label}
          aria-checked={selected === code}
          role="radio"
          title={label}
        >
          {emoji}
        </button>
      ))}
    </div>
  );
}
