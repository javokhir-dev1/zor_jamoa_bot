import { useEffect, useState } from "react";
import { createBulkOrder } from "../api/orders";
import { getMyDeptMembers } from "../api/departments";
import MemberRow from "../components/MemberRow";
import Button from "../components/Button";
import { useTelegram } from "../hooks/useTelegram";

const MEALS = [
  { value: "tushlik", label: "🍱 Tushlik (Обед)" },
  { value: "kechki_ovqat", label: "🍽 Kechki ovqat (Ужин)" },
];

export default function DeptHeadPage() {
  const { showConfirm, showAlert, haptic } = useTelegram();

  const [members, setMembers]       = useState([]);
  const [selectedMeal, setMeal]     = useState("tushlik");
  const [checked, setChecked]       = useState(new Set());
  const [loading, setLoading]       = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult]         = useState(null);

  useEffect(() => {
    setLoading(true);
    getMyDeptMembers()
      .then((data) => {
        setMembers(data);
        setChecked(new Set());
      })
      .finally(() => setLoading(false));
  }, [selectedMeal]);

  function toggleMember(id) {
    setChecked((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function selectAll() {
    const eligible = members
      .filter((m) =>
        selectedMeal === "tushlik" ? !m.has_lunch : !m.has_dinner
      )
      .map((m) => m.id);
    setChecked(new Set(eligible));
  }

  async function handleSubmit() {
    const ids = [...checked];
    if (!ids.length) {
      showAlert("Hech kimni tanlamadingiz.");
      return;
    }

    showConfirm(
      `${ids.length} ta hodimga ${selectedMeal === "tushlik" ? "tushlik" : "kechki ovqat"} buyurtma berilsinmi?`,
      async (ok) => {
        if (!ok) return;
        setSubmitting(true);
        try {
          const res = await createBulkOrder(ids, selectedMeal);
          haptic("medium");
          setResult(res);
          setChecked(new Set());
          // Ro'yxatni yangilash
          const updated = await getMyDeptMembers();
          setMembers(updated);
        } catch (e) {
          showAlert(e?.response?.data?.detail ?? "Xatolik yuz berdi.");
        } finally {
          setSubmitting(false);
        }
      }
    );
  }

  const eligibleCount = members.filter((m) =>
    selectedMeal === "tushlik" ? !m.has_lunch : !m.has_dinner
  ).length;

  return (
    <div style={{ padding: "20px 16px", maxWidth: 480, margin: "0 auto" }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
        👥 Bo'lim uchun buyurtma
      </h1>
      <p style={{ color: "var(--tg-theme-hint-color)", fontSize: 13, marginBottom: 20 }}>
        Faqat buyurtma bermaganlarga buyurtma bera olasiz
      </p>

      {/* Ovqat tanlash */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {MEALS.map((m) => (
          <button
            key={m.value}
            onClick={() => { setMeal(m.value); setChecked(new Set()); setResult(null); }}
            style={{
              flex: 1,
              padding: "10px 8px",
              borderRadius: "var(--radius-sm)",
              fontWeight: 600,
              fontSize: 13,
              background:
                selectedMeal === m.value
                  ? "var(--accent)"
                  : "var(--tg-theme-secondary-bg-color)",
              color: selectedMeal === m.value ? "#fff" : "var(--tg-theme-text-color)",
            }}
          >
            {m.label}
          </button>
        ))}
      </div>

      {/* Natija banner */}
      {result && (
        <div
          style={{
            padding: "10px 14px",
            background: "rgba(67,160,71,0.1)",
            borderRadius: "var(--radius-sm)",
            color: "var(--success)",
            fontWeight: 600,
            marginBottom: 16,
            fontSize: 14,
          }}
        >
          ✅ {result.created_count} ta buyurtma berildi
          {result.skipped_count > 0 && ` · ${result.skipped_count} ta o'tkazib yuborildi`}
        </div>
      )}

      {/* A'zolar ro'yxati */}
      {loading ? (
        <p style={{ color: "var(--tg-theme-hint-color)", textAlign: "center", padding: 32 }}>
          ⏳ Yuklanmoqda...
        </p>
      ) : members.length === 0 ? (
        <p style={{ color: "var(--tg-theme-hint-color)", textAlign: "center", padding: 32 }}>
          Bo'limda hodim yo'q.
        </p>
      ) : (
        <>
          {/* Hammasini tanlash */}
          {eligibleCount > 0 && (
            <button
              onClick={selectAll}
              style={{
                width: "100%",
                padding: "9px",
                marginBottom: 10,
                borderRadius: "var(--radius-sm)",
                background: "transparent",
                border: "1.5px dashed var(--accent)",
                color: "var(--accent)",
                fontWeight: 600,
                fontSize: 13,
              }}
            >
              Hammasini tanlash ({eligibleCount} ta)
            </button>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {members.map((m) => (
              <MemberRow
                key={m.id}
                member={m}
                selectedMeal={selectedMeal}
                checked={checked.has(m.id)}
                onToggle={toggleMember}
              />
            ))}
          </div>

          {/* Yuborish tugmasi */}
          {checked.size > 0 && (
            <div style={{ marginTop: 20 }}>
              <Button
                fullWidth
                loading={submitting}
                onClick={handleSubmit}
              >
                {checked.size} ta hodimga buyurtma berish
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
