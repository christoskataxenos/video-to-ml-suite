/**
 * ParentDashboard — Κέντρο ελέγχου γονέα.
 * Ο γονέας ρυθμίζει: γλώσσα, mode annotation, στυλ UI, interaction mode.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import LanguagePicker from "../components/LanguagePicker";
import ModeSelector from "../components/ModeSelector";
import { getParentSettings, saveParentSettings } from "../lib/api";
import type { ParentSettings } from "../lib/api";

export default function ParentDashboard() {
  const navigate = useNavigate();

  // Κατάσταση ρυθμίσεων
  const [settings, setSettings] = useState<ParentSettings>({
    child_name: "Explorer",
    language: "en",
    annotation_mode: "sticker",
    ui_style: "mascot",
    interaction_mode: "storyteller",
  });
  const [showToast, setShowToast] = useState(false);
  const [loading, setLoading] = useState(true);

  // Φόρτωση ρυθμίσεων κατά το mount
  useEffect(() => {
    getParentSettings()
      .then((data) => {
        setSettings(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Αποθήκευση ρυθμίσεων
  const handleSave = async () => {
    await saveParentSettings(settings);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  // Εκκίνηση Kids Mode
  const handleLaunch = async () => {
    await saveParentSettings(settings);
    navigate("/kids");
  };

  // Ενημέρωση μεμονωμένου πεδίου
  const update = <K extends keyof ParentSettings>(key: K, value: ParentSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div className="parent-dashboard" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ fontSize: "1.2rem", opacity: 0.6 }}>Loading...</p>
      </div>
    );
  }

  return (
    <div className="parent-dashboard">
      <div className="app-container">
        {/* Header */}
        <div className="page-header">
          <h1>🧠 PolyMind</h1>
          <p className="subtitle" style={{ color: "var(--text-muted)" }}>
            Parent Dashboard
          </p>
        </div>

        {/* Γλώσσα */}
        <div className="section">
          <div className="form-group">
            <span className="form-label">Language</span>
            <LanguagePicker
              selected={settings.language}
              onChange={(lang) => update("language", lang)}
            />
          </div>
        </div>

        {/* Όνομα παιδιού */}
        <div className="section">
          <div className="form-group">
            <label className="form-label" htmlFor="child-name">Child's Name</label>
            <input
              id="child-name"
              className="form-input"
              type="text"
              value={settings.child_name}
              onChange={(e) => update("child_name", e.target.value)}
              placeholder="Enter your child's name..."
              maxLength={50}
            />
          </div>
        </div>

        {/* Annotation Mode */}
        <div className="section">
          <ModeSelector
            label="Game Mode"
            selected={settings.annotation_mode}
            onChange={(v) => update("annotation_mode", v as ParentSettings["annotation_mode"])}
            options={[
              {
                value: "sticker",
                label: "Sticker Mode",
                description: "Place stickers on objects — best for younger kids",
                icon: "🏷️",
              },
              {
                value: "catch",
                label: "Catch the Object",
                description: "Tap objects as they appear — best for older kids",
                icon: "🎯",
              },
            ]}
          />
        </div>

        {/* UI Style */}
        <div className="section">
          <ModeSelector
            label="Interface Style"
            selected={settings.ui_style}
            onChange={(v) => update("ui_style", v as ParentSettings["ui_style"])}
            options={[
              {
                value: "mascot",
                label: "Mascot Guide",
                description: "A friendly character guides your child step by step",
                icon: "🤖",
              },
              {
                value: "icon",
                label: "Icon-First",
                description: "Big colorful buttons with no text — visual learning",
                icon: "🎨",
              },
              {
                value: "audio",
                label: "Audio-Driven",
                description: "Every button speaks its name — helps with vocabulary",
                icon: "🔊",
              },
            ]}
          />
        </div>

        {/* Interaction Mode */}
        <div className="section">
          <ModeSelector
            label="After Training"
            selected={settings.interaction_mode}
            onChange={(v) => update("interaction_mode", v as ParentSettings["interaction_mode"])}
            options={[
              {
                value: "logic_blocks",
                label: "Logic Blocks",
                description: "If the AI sees X → Do Y (like Scratch)",
                icon: "🧩",
              },
              {
                value: "storyteller",
                label: "Storyteller",
                description: "Objects come alive and talk to your child",
                icon: "📖",
              },
            ]}
          />
        </div>

        {/* Action Buttons */}
        <div className="section" style={{ display: "flex", gap: "var(--space-md)", flexWrap: "wrap" }}>
          <button className="btn btn-secondary" onClick={handleSave}>
            💾 Save Settings
          </button>
          <button className="btn btn-primary btn-large" onClick={handleLaunch}>
            🚀 Launch Kids Mode
          </button>
        </div>
      </div>

      {/* Toast notification */}
      {showToast && <div className="toast">✅ Settings saved!</div>}
    </div>
  );
}
