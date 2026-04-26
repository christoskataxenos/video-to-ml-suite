/**
 * MascotBubble — Η μασκότ "Poly" με speech bubble.
 * Χρησιμοποιείται για να καθοδηγεί το παιδί.
 */

interface MascotBubbleProps {
  message: string;
  emoji?: string;
}

export default function MascotBubble({ message, emoji = "🤖" }: MascotBubbleProps) {
  return (
    <div className="mascot-container">
      <div className="mascot-avatar" aria-hidden="true">
        {emoji}
      </div>
      <div className="mascot-bubble">
        <p>{message}</p>
      </div>
    </div>
  );
}
