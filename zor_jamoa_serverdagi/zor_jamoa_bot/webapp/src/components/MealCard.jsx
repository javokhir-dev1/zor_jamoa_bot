/**
 * Tushlik yoki kechki ovqat kartochkasi.
 * status: "none" | "ordered" | "disabled"
 */
export default function MealCard({ type, status, onOrder }) {
  const isOrdered  = status === "ordered";
  const isDisabled = status === "disabled";

  const config = {
    tushlik: {
      emoji: "🍱",
      label: "Tushlik",
      sub: "Обед",
    },
    kechki_ovqat: {
      emoji: "🍽",
      label: "Kechki ovqat",
      sub: "Ужин",
    },
  }[type];

  return (
    <div
      style={{
        background: isOrdered
          ? "rgba(67, 160, 71, 0.1)"
          : "var(--tg-theme-secondary-bg-color)",
        border: isOrdered
          ? "2px solid var(--success)"
          : "2px solid transparent",
        borderRadius: "var(--radius)",
        padding: "20px 16px",
        display: "flex",
        alignItems: "center",
        gap: 16,
        opacity: isDisabled ? 0.45 : 1,
      }}
    >
      <span style={{ fontSize: 36 }}>{config.emoji}</span>

      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: 16 }}>{config.label}</div>
        <div style={{ color: "var(--tg-theme-hint-color)", fontSize: 13 }}>
          {config.sub}
        </div>
      </div>

      {isOrdered ? (
        <span
          style={{
            background: "var(--success)",
            color: "#fff",
            borderRadius: 20,
            padding: "4px 12px",
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          ✓ Buyurtma berildi
        </span>
      ) : (
        <button
          onClick={onOrder}
          disabled={isDisabled}
          style={{
            background: isDisabled ? "#ccc" : "var(--accent)",
            color: "#fff",
            border: "none",
            borderRadius: 20,
            padding: "6px 16px",
            fontSize: 13,
            fontWeight: 600,
            cursor: isDisabled ? "default" : "pointer",
          }}
        >
          Buyurtma
        </button>
      )}
    </div>
  );
}
