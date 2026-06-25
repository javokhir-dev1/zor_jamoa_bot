import { useEffect, useState } from "react";
import { getReport } from "../../api/admin";
import {
  IconBarChart, IconRefresh, IconCalendar, IconCheckCircle,
  IconSun, IconMoon, IconBuilding, IconAlertCircle, IconCheck,
} from "../../components/Icons";
import { PageLoader, Spinner } from "../../components/Spinner";

export default function ReportPage() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [tab, setTab]         = useState("tushlik");
  const [force, setForce]     = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = (forceLoad = false) => {
    setLoading(true);
    setError(null);
    getReport(forceLoad)
      .then(setData)
      .catch(e => setError(e?.response?.data?.detail || "Xatolik"))
      .finally(() => setLoading(false));
  };

  async function handleRefresh() {
    setRefreshing(true);
    try { await getReport(force).then(setData); setError(null); }
    catch (e) { setError(e?.response?.data?.detail || "Xatolik"); }
    finally { setRefreshing(false); }
  }

  useEffect(() => { load(false); }, []);

  function toggleForce() {
    const next = !force;
    setForce(next);
    load(next);
  }

  const sections = tab === "tushlik" ? data?.lunch : data?.dinner;
  const total    = tab === "tushlik" ? data?.lunch_total : data?.dinner_total;

  return (
    <div style={page}>
      {/* Header */}
      <div style={topRow}>
        <div style={titleRow}>
          <IconBarChart size={20} color="var(--accent)" />
          <span style={titleText}>Kunlik hisobot</span>
        </div>
        <button style={btnRefresh} onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? <Spinner size={18} /> : <IconRefresh size={18} color="var(--tg-theme-hint-color)" />}
        </button>
      </div>

      {/* Date badge */}
      {data && (
        <div style={dateBadge}>
          <IconCalendar size={13} color="var(--tg-theme-hint-color)" />
          <span>{data.report_date}</span>
          <span style={separator}>·</span>
          {data.is_final
            ? <><IconCheckCircle size={13} color="var(--success)" /><span style={{ color: "var(--success)" }}>Final</span></>
            : <span style={{ color: "var(--tg-theme-hint-color)" }}>Kutilmoqda</span>
          }
        </div>
      )}

      {/* Test toggle */}
      <label style={toggleRow}>
        <div style={toggle(force)} onClick={toggleForce}>
          <div style={toggleThumb(force)} />
        </div>
        <span style={{ fontSize: 12, color: "var(--tg-theme-hint-color)", marginLeft: 8 }}>
          Test rejimi (vaqtsiz ko'rish)
        </span>
      </label>

      {loading ? <PageLoader /> : error ? (
        <div style={errBox}>
          <IconAlertCircle size={18} color="var(--danger)" />
          <div>
            <div style={{ fontWeight: 600 }}>{error}</div>
            {error.includes("13:59") && (
              <div style={{ fontSize: 12, marginTop: 4 }}>Test rejimini yoqing yoki 13:59 dan keyin keling.</div>
            )}
          </div>
        </div>
      ) : (
        <>
          {/* Tabs */}
          <div style={tabs}>
            <button style={tab === "tushlik" ? activeTab : inactiveTab} onClick={() => setTab("tushlik")}>
              <IconSun size={14} color={tab === "tushlik" ? "#fff" : "var(--tg-theme-hint-color)"} />
              Tushlik ({data?.lunch_total ?? 0})
            </button>
            <button style={tab === "kechki_ovqat" ? activeTab : inactiveTab} onClick={() => setTab("kechki_ovqat")}>
              <IconMoon size={14} color={tab === "kechki_ovqat" ? "#fff" : "var(--tg-theme-hint-color)"} />
              Kechki ({data?.dinner_total ?? 0})
            </button>
          </div>

          {sections?.length === 0 ? <Empty text="Buyurtma yo'q" /> : (
            sections?.map(s => (
              <div key={s.department} style={deptCard}>
                <div style={deptHeader}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <IconBuilding size={14} color="var(--tg-theme-hint-color)" />
                    <span>{s.department}</span>
                  </div>
                  <span style={badge}>{s.count}</span>
                </div>
                {s.members.map((m, i) => (
                  <div key={m.user_id} style={memberRow(i)}>
                    <span>{m.full_name}</span>
                    {m.is_taken
                      ? <div style={takenChip}><IconCheck size={11} color="var(--success)" /><span>Olindi</span></div>
                      : <span style={{ fontSize: 11, color: "var(--tg-theme-hint-color)" }}>Kutmoqda</span>
                    }
                  </div>
                ))}
              </div>
            ))
          )}

          {sections && sections.length > 0 && (
            <div style={totalRow}>Jami: <strong>{total}</strong> ta buyurtma</div>
          )}
        </>
      )}
    </div>
  );
}

const page     = { padding: "16px 14px", maxWidth: 520, margin: "0 auto" };
const topRow   = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 };
const titleRow = { display: "flex", alignItems: "center", gap: 8 };
const titleText = { fontSize: 18, fontWeight: 700 };
const btnRefresh = { width: 36, height: 36, borderRadius: 10, background: "var(--tg-theme-secondary-bg-color)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const dateBadge = { display: "flex", alignItems: "center", gap: 5, background: "var(--tg-theme-secondary-bg-color)", borderRadius: 8, padding: "6px 12px", fontSize: 12, marginBottom: 10, width: "fit-content" };
const separator = { color: "var(--tg-theme-hint-color)", margin: "0 2px" };
const toggleRow = { display: "flex", alignItems: "center", cursor: "pointer", marginBottom: 14 };
const toggle    = on => ({ width: 36, height: 20, borderRadius: 10, background: on ? "var(--accent)" : "var(--tg-theme-secondary-bg-color)", position: "relative", transition: "background 0.2s", flexShrink: 0, cursor: "pointer" });
const toggleThumb = on => ({ position: "absolute", top: 2, left: on ? 18 : 2, width: 16, height: 16, borderRadius: 8, background: "#fff", transition: "left 0.2s", boxShadow: "0 1px 3px rgba(0,0,0,0.2)" });
const tabs     = { display: "flex", gap: 8, marginBottom: 12 };
const activeTab   = { flex: 1, padding: "10px 0", borderRadius: 10, background: "var(--accent)", color: "#fff", fontWeight: 700, fontSize: 13, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 };
const inactiveTab = { flex: 1, padding: "10px 0", borderRadius: 10, background: "var(--tg-theme-secondary-bg-color)", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 };
const deptCard  = { background: "var(--tg-theme-secondary-bg-color)", borderRadius: 12, marginBottom: 10, overflow: "hidden" };
const deptHeader = { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", fontWeight: 700, fontSize: 14, borderBottom: "1px solid rgba(0,0,0,0.06)" };
const badge    = { background: "var(--accent)", color: "#fff", borderRadius: 20, padding: "1px 9px", fontSize: 12 };
const memberRow = i => ({ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 14px", fontSize: 13, background: i % 2 === 0 ? "transparent" : "rgba(0,0,0,0.025)" });
const takenChip = { display: "flex", alignItems: "center", gap: 3, fontSize: 11, color: "var(--success)" };
const totalRow = { textAlign: "right", fontSize: 13, color: "var(--tg-theme-hint-color)", marginTop: 4 };
const errBox   = { display: "flex", alignItems: "flex-start", gap: 10, background: "rgba(229,57,53,0.08)", color: "var(--danger)", borderRadius: 12, padding: "14px 16px", fontSize: 14 };
function Empty({ text }) { return <div style={{ textAlign: "center", padding: 40, color: "var(--tg-theme-hint-color)" }}>{text}</div>; }
