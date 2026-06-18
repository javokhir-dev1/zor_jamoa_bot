import { useEffect, useState } from "react";
import { createOrder, getMyOrders } from "../api/orders";
import MealCard from "../components/MealCard";
import { useTelegram } from "../hooks/useTelegram";

export default function OrderPage() {
  const { user, showConfirm, haptic } = useTelegram();

  const [myOrders, setMyOrders]   = useState(null);  // { has_lunch, has_dinner, order_date }
  const [loading, setLoading]     = useState(true);
  const [submitting, setSubmitting] = useState(null); // "tushlik" | "kechki_ovqat"
  const [error, setError]         = useState(null);

  useEffect(() => {
    getMyOrders()
      .then(setMyOrders)
      .catch(() => setError("Ma'lumot yuklab bo'lmadi."))
      .finally(() => setLoading(false));
  }, []);

  async function handleOrder(meal_type) {
    const label = meal_type === "tushlik" ? "tushlik" : "kechki ovqat";

    showConfirm(
      `Ertangi kun uchun 1 kishilik ${label}ni tasdiqlaysizmi?`,
      async (confirmed) => {
        if (!confirmed) return;

        setSubmitting(meal_type);
        setError(null);
        try {
          await createOrder(meal_type);
          haptic("medium");
          const updated = await getMyOrders();
          setMyOrders(updated);
        } catch (e) {
          const msg = e?.response?.data?.detail ?? "Xatolik yuz berdi.";
          setError(msg);
        } finally {
          setSubmitting(null);
        }
      }
    );
  }

  if (loading) {
    return (
      <div style={centered}>
        <span style={{ fontSize: 36 }}>⏳</span>
        <p style={{ color: "var(--tg-theme-hint-color)" }}>Yuklanmoqda...</p>
      </div>
    );
  }

  const tomorrow = myOrders?.order_date
    ? formatDate(myOrders.order_date)
    : "ertangi kun";

  return (
    <div style={{ padding: "20px 16px", maxWidth: 480, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700 }}>🍽 Ovqat buyurtma qilish</h1>
        <p style={{ color: "var(--tg-theme-hint-color)", fontSize: 13, marginTop: 4 }}>
          {tomorrow} uchun buyurtma
        </p>
        {user && (
          <p style={{ fontSize: 13, marginTop: 2, color: "var(--tg-theme-hint-color)" }}>
            👤 {user.first_name} {user.last_name ?? ""}
          </p>
        )}
      </div>

      {/* Xato */}
      {error && (
        <div
          style={{
            background: "rgba(229,57,53,0.1)",
            border: "1px solid var(--danger)",
            borderRadius: "var(--radius-sm)",
            padding: "10px 14px",
            color: "var(--danger)",
            fontSize: 14,
            marginBottom: 16,
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {/* Kartochkalar */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {["tushlik", "kechki_ovqat"].map((meal) => {
          const isOrdered =
            meal === "tushlik" ? myOrders?.has_lunch : myOrders?.has_dinner;

          return (
            <MealCard
              key={meal}
              type={meal}
              status={
                isOrdered
                  ? "ordered"
                  : submitting === meal
                  ? "disabled"
                  : "none"
              }
              onOrder={() => handleOrder(meal)}
            />
          );
        })}
      </div>

      {/* Ikkalasi ham buyurtma qilinsa */}
      {myOrders?.has_lunch && myOrders?.has_dinner && (
        <div
          style={{
            marginTop: 24,
            padding: "14px 16px",
            background: "rgba(67,160,71,0.1)",
            borderRadius: "var(--radius)",
            textAlign: "center",
            color: "var(--success)",
            fontWeight: 600,
          }}
        >
          ✅ Barcha buyurtmalar berildi!
        </div>
      )}
    </div>
  );
}

const centered = {
  minHeight: "60vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 12,
};

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("uz-UZ", {
    day: "numeric",
    month: "long",
    weekday: "long",
  });
}
