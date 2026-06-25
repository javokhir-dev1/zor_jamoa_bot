import { useEffect, useState } from "react";
import { getDistribution, markTaken, getAdminDepts } from "../../api/admin";
import {
  IconUtensilsCrossed, IconRefresh, IconBuilding,
  IconSun, IconMoon, IconCheck, IconCheckCircle,
} from "../../components/Icons";
import { PageLoader, Spinner } from "../../components/Spinner";

export default function DistributionPage() {
  const [orders, setOrders]   = useState([]);
  const [depts, setDepts]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deptFilter, setDeptFilter] = useState("");
  const [mealFilter, setMealFilter] = useState("");

  const load = () => {
    setLoading(true);
    Promise.all([getDistribution(deptFilter || null), getAdminDepts()])
      .then(([o, d]) => { setOrders(o); setDepts(d); })
      .finally(() => setLoading(false));
  };

  async function handleRefresh() {
    setRefreshing(true);
    try {
      const [o, d] = await Promise.all([getDistribution(deptFilter || null), getAdminDepts()]);
      setOrders(o); setDepts(d);
    } finally { setRefreshing(false); }
  }

  useEffect(load, [deptFilter]);

  async function handleTaken(order_id) {
    await markTaken(order_id);
    setOrders(prev => prev.map(o =>
      o.order_id === order_id ? { ...o, is_taken: true, taken_at: new Date().toTimeString().slice(0, 5) } : o
    ));
  }

  const filtered = mealFilter ? orders.filter(o => o.meal_type === mealFilter) : orders;
  const taken    = filtered.filter(o => o.is_taken).length;
  const pending  = filtered.filter(o => !o.is_taken).length;

  return (
    <div style={page}>
      {/* Header */}
      <div style={topRow}>
        <div style={titleRow}>
          <IconUtensilsCrossed size={20} color="var(--accent)" />
          <span style={titleText}>Tarqatish</span>
        </div>
        <button style={btnRefresh} onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? <Spinner size={18} /> : <IconRefresh size={18} color="var(--tg-theme-hint-color)" />}
        </button>
      </div>

      {/* Stats */}
      {!loading && (
        <div style={statsRow}>
          <div style={statTaken}>
            <IconCheckCircle size={16} color="var(--success)" />
            <span>{taken} olindi</span>
          </div>
          <div style={statPending}>
            <span style={dot} />
            <span>{pending} kutmoqda</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={filterRow}>
        <div style={filterWrap}>
          <IconBuilding size={14} color="var(--tg-theme-hint-color)" />
          <select style={filterSelect} value={deptFilter} onChange={e => setDeptFilter(e.target.value)}>
            <option value="">Barcha bo'limlar</option>
            {depts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
        <div style={filterWrap}>
          <IconSun size={14} color="var(--tg-theme-hint-color)" />
          <select style={filterSelect} value={mealFilter} onChange={e => setMealFilter(e.target.value)}>
            <option value="">Barcha ovqatlar</option>
            <option value="tushlik">Tushlik</option>
            <option value="kechki_ovqat">Kechki ovqat</option>
          </select>
        </div>
      </div>

      {loading ? <PageLoader /> : filtered.length === 0 ? <Empty text="Buyurtma yo'q" /> : (
        filtered.map(o => (
          <div key={o.order_id} style={card(o.is_taken)}>
            <div style={cardRow}>
              <div style={{ flex: 1 }}>
                <div style={name}>{o.full_name}</div>
                <div style={metaRow}>
                  <IconBuilding size={12} color="var(--tg-theme-hint-color)" />
                  <span style={metaText}>{o.department}</span>
                </div>
                <div style={metaRow}>
                  {o.meal_type === "tushlik"
                    ? <IconSun  size={12} color="var(--tg-theme-hint-color)" />
                    : <IconMoon size={12} color="var(--tg-theme-hint-color)" />
                  }
                  <span style={metaText}>{o.meal_type === "tushlik" ? "Tushlik" : "Kechki ovqat"}</span>
                </div>
              </div>
              <div>
                {o.is_taken ? (
                  <div style={takenBadge}>
                    <IconCheck size={14} color="var(--success)" />
                    <span>{o.taken_at}</span>
                  </div>
                ) : (
                  <button style={btnTake} onClick={() => handleTaken(o.order_id)}>
                    Berish
                  </button>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

const page     = { padding: "16px 14px", maxWidth: 520, margin: "0 auto" };
const topRow   = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 };
const titleRow = { display: "flex", alignItems: "center", gap: 8 };
const titleText = { fontSize: 18, fontWeight: 700 };
const btnRefresh = { width: 36, height: 36, borderRadius: 10, background: "var(--tg-theme-secondary-bg-color)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const statsRow = { display: "flex", gap: 8, marginBottom: 12 };
const statTaken   = { flex: 1, borderRadius: 10, padding: "9px 12px", background: "rgba(67,160,71,0.1)", color: "var(--success)", fontWeight: 600, fontSize: 13, display: "flex", alignItems: "center", gap: 6 };
const statPending = { flex: 1, borderRadius: 10, padding: "9px 12px", background: "rgba(255,152,0,0.1)", color: "#f57c00", fontWeight: 600, fontSize: 13, display: "flex", alignItems: "center", gap: 6 };
const dot      = { width: 8, height: 8, borderRadius: 4, background: "#f57c00", flexShrink: 0 };
const filterRow = { display: "flex", gap: 8, marginBottom: 12 };
const filterWrap = { flex: 1, display: "flex", alignItems: "center", gap: 6, background: "var(--tg-theme-secondary-bg-color)", borderRadius: 10, padding: "0 10px" };
const filterSelect = { flex: 1, padding: "9px 0", border: "none", background: "transparent", fontSize: 13, outline: "none" };
const card = taken => ({
  background: taken ? "rgba(67,160,71,0.06)" : "var(--tg-theme-secondary-bg-color)",
  borderRadius: 12, padding: "12px 14px", marginBottom: 8,
  borderLeft: taken ? "3px solid var(--success)" : "3px solid transparent",
});
const cardRow  = { display: "flex", justifyContent: "space-between", alignItems: "center" };
const name     = { fontWeight: 700, fontSize: 14, marginBottom: 4 };
const metaRow  = { display: "flex", alignItems: "center", gap: 4, marginTop: 2 };
const metaText = { fontSize: 12, color: "var(--tg-theme-hint-color)" };
const btnTake  = { padding: "9px 16px", borderRadius: 9, background: "var(--accent)", color: "#fff", fontWeight: 700, fontSize: 13, border: "none", cursor: "pointer" };
const takenBadge = { display: "flex", alignItems: "center", gap: 4, fontSize: 13, fontWeight: 600, color: "var(--success)" };
function Empty({ text }) { return <div style={{ textAlign: "center", padding: 40, color: "var(--tg-theme-hint-color)" }}>{text}</div>; }
