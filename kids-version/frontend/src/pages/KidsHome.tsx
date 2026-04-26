/**
 * KidsHome — Η αρχική σελίδα που βλέπει το παιδί.
 * Δείχνει τη μασκότ, χαιρετισμό στη σωστή γλώσσα, και πόντους.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MascotBubble from "../components/MascotBubble";
import { getChildSession, getStrings } from "../lib/api";
import type { ChildSession } from "../lib/api";

/** Τύπος για τα child strings */
interface ChildStrings {
  home_title: string;
  start_button: string;
  score_label: string;
  back_button: string;
}

export default function KidsHome() {
  const navigate = useNavigate();

  const [session, setSession] = useState<ChildSession | null>(null);
  const [greeting, setGreeting] = useState("Hi! I'm Poly, your AI friend!");
  const [strings, setStrings] = useState<ChildStrings>({
    home_title: "Let's Play!",
    start_button: "Start!",
    score_label: "Stars",
    back_button: "Back",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSession() {
      try {
        // Φόρτωση session δεδομένων
        const sessionData = await getChildSession();
        setSession(sessionData);

        // Φόρτωση strings στη σωστή γλώσσα
        const langStrings = await getStrings(sessionData.language);
        const mascotGreeting = (langStrings as Record<string, string>).mascot_greeting || greeting;
        const mascotReady = (langStrings as Record<string, string>).mascot_ready || "";

        // Αντικατάσταση {name} με το πραγματικό όνομα
        setGreeting(
          mascotGreeting.replace("{name}", sessionData.child_name) +
          (mascotReady ? " " + mascotReady : "")
        );

        // Φόρτωση child-specific strings
        const childStrings = (langStrings as Record<string, Record<string, string>>).child;
        if (childStrings) {
          setStrings(childStrings as unknown as ChildStrings);
        }
      } catch (err) {
        console.error("Failed to load session:", err);
      } finally {
        setLoading(false);
      }
    }
    loadSession();
  }, []);

  if (loading) {
    return (
      <div className="kids-home">
        <div className="mascot-avatar" style={{ width: 120, height: 120, fontSize: "4rem" }}>
          🤖
        </div>
        <p style={{ fontSize: "1.5rem", opacity: 0.6 }}>Loading...</p>
      </div>
    );
  }

  return (
    <div className="kids-home">
      {/* Mascot χαιρετισμός */}
      <MascotBubble message={greeting} />

      {/* Τίτλος */}
      <h1>{strings.home_title}</h1>

      {/* Πόντοι / Αστέρια */}
      {session && (
        <div className="kids-score">
          ⭐ {session.total_score} {strings.score_label}
        </div>
      )}

      {/* Κουμπί εκκίνησης (Phase 2 θα ανοίγει τα παιχνίδια) */}
      <button className="btn btn-kids" onClick={() => alert("🎮 Coming in Phase 2!")}>
        {strings.start_button}
      </button>

      {/* Κουμπί επιστροφής στο Parent Dashboard */}
      <button
        className="btn btn-secondary"
        onClick={() => navigate("/")}
        style={{ marginTop: "var(--space-md)" }}
      >
        🔙 {strings.back_button}
      </button>
    </div>
  );
}
