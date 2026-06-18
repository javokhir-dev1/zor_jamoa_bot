export default function Button({ children, onClick, variant = "primary", disabled, loading, fullWidth }) {
  const styles = {
    primary: {
      background: "var(--accent)",
      color: "#fff",
    },
    secondary: {
      background: "var(--tg-theme-secondary-bg-color)",
      color: "var(--tg-theme-text-color)",
    },
    danger: {
      background: "var(--danger)",
      color: "#fff",
    },
    success: {
      background: "var(--success)",
      color: "#fff",
    },
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        ...styles[variant],
        width: fullWidth ? "100%" : "auto",
        padding: "13px 20px",
        borderRadius: "var(--radius)",
        fontWeight: 600,
        fontSize: 15,
        opacity: disabled || loading ? 0.5 : 1,
        transition: "opacity 0.15s, transform 0.1s",
      }}
    >
      {loading ? "⏳ Yuborilmoqda..." : children}
    </button>
  );
}
