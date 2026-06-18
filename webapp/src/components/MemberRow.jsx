/**
 * Bo'lim rahbari sahifasidagi a'zo qatori.
 * has_lunch / has_dinner — yashil/qizil status
 */
export default function MemberRow({ member, selectedMeal, checked, onToggle }) {
  const hasOrder =
    selectedMeal === "tushlik" ? member.has_lunch : member.has_dinner;

  return (
    <div
      onClick={() => !hasOrder && onToggle(member.id)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 16px",
        borderRadius: "var(--radius-sm)",
        background: "var(--tg-theme-secondary-bg-color)",
        cursor: hasOrder ? "default" : "pointer",
        opacity: hasOrder ? 0.6 : 1,
        border: checked ? "2px solid var(--accent)" : "2px solid transparent",
      }}
    >
      {/* Checkbox */}
      <div
        style={{
          width: 22,
          height: 22,
          borderRadius: 6,
          border: hasOrder ? "none" : "2px solid var(--accent)",
          background: hasOrder
            ? "var(--success)"
            : checked
            ? "var(--accent)"
            : "transparent",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          color: "#fff",
          fontSize: 13,
        }}
      >
        {hasOrder ? "✓" : checked ? "✓" : ""}
      </div>

      {/* Ism */}
      <span style={{ flex: 1, fontWeight: 500 }}>{member.full_name}</span>

      {/* Status pill */}
      <span
        style={{
          fontSize: 11,
          fontWeight: 600,
          padding: "2px 10px",
          borderRadius: 20,
          background: hasOrder ? "var(--success)" : "var(--danger)",
          color: "#fff",
        }}
      >
        {hasOrder ? "Buyurtma bor" : "Buyurtma yo'q"}
      </span>
    </div>
  );
}
