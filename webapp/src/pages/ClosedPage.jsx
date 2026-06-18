export default function ClosedPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 24px",
        textAlign: "center",
        gap: 16,
      }}
    >
      <span style={{ fontSize: 64 }}>⏰</span>
      <h2 style={{ fontSize: 20, fontWeight: 700 }}>Buyurtma yopiq</h2>
      <p style={{ color: "var(--tg-theme-hint-color)", fontSize: 15 }}>
        Ertangi kun uchun buyurtma berish yakunlandi.
        <br />
        Iltimos, buyurtmalaringizni har kuni{" "}
        <strong>13:55</strong> dan kechiktirmasdan yozib qoldiring.
      </p>
    </div>
  );
}
