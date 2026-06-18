import { useEffect, useState } from "react";
import { getApplications, approveUser, rejectUser } from "../../api/admin";
import { IconCheck, IconX } from "../../components/Icons";

export default function ApplicationsPage() {
  const [list, setList]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing]   = useState(null); // id of item being acted on

  const load = () => {
    setLoading(true);
    getApplications().then(setList).finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function handle(id, action) {
    setActing(id);
    await (action === "approve" ? approveUser(id) : rejectUser(id));
    setActing(null);
    load();
  }

  if (loading) return <Loader />;

  return (
    <div style={page}>
      <div style={header}>
        <span style={titleText}>Arizalar</span>
        {list.length > 0 && <Badge>{list.length}</Badge>}
      </div>

      {list.length === 0 ? (
        <Empty text="Kutayotgan ariza yo'q" />
      ) : (
        list.map(u => (
          <div key={u.id} style={card}>
            <div style={cardTop}>
              <div style={avatar}>{u.full_name[0]}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 15 }}>{u.full_name}</div>
                <div style={meta}>{u.phone_number || "—"}</div>
              </div>
            </div>
            <div style={infoRow}>
              <InfoChip label="Bo'lim" value={u.department || "—"} />
              <InfoChip label="Telegram ID" value={u.telegram_id} mono />
            </div>
            <div style={btnRow}>
              <button
                style={btnSuccess}
                disabled={acting === u.id}
                onClick={() => handle(u.id, "approve")}
              >
                <IconCheck size={16} color="#fff" />
                Tasdiqlash
              </button>
              <button
                style={btnDanger}
                disabled={acting === u.id}
                onClick={() => handle(u.id, "reject")}
              >
                <IconX size={16} color="#fff" />
                Rad etish
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function InfoChip({ label, value, mono }) {
  return (
    <div style={chip}>
      <span style={chipLabel}>{label}</span>
      <span style={{ ...(mono ? { fontFamily: "monospace", fontSize: 11 } : { fontSize: 12 }) }}>{value}</span>
    </div>
  );
}

function Badge({ children }) {
  return <span style={{ background: "var(--danger)", color: "#fff", borderRadius: 20, padding: "2px 9px", fontSize: 12, marginLeft: 8 }}>{children}</span>;
}
function Loader() { return <div style={{ textAlign: "center", padding: 40, color: "var(--tg-theme-hint-color)" }}>Yuklanmoqda...</div>; }
function Empty({ text }) { return <div style={{ textAlign: "center", padding: 40, color: "var(--tg-theme-hint-color)" }}>{text}</div>; }

const page     = { padding: "16px 14px", maxWidth: 520, margin: "0 auto" };
const header   = { display: "flex", alignItems: "center", marginBottom: 16 };
const titleText = { fontSize: 18, fontWeight: 700 };
const card     = { background: "var(--tg-theme-secondary-bg-color)", borderRadius: 14, padding: "14px 16px", marginBottom: 10 };
const cardTop  = { display: "flex", alignItems: "center", gap: 12, marginBottom: 10 };
const avatar   = { width: 40, height: 40, borderRadius: 20, background: "var(--accent)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 18, flexShrink: 0 };
const meta     = { fontSize: 12, color: "var(--tg-theme-hint-color)", marginTop: 2 };
const infoRow  = { display: "flex", gap: 8, marginBottom: 12 };
const chip     = { flex: 1, background: "var(--tg-theme-bg-color)", borderRadius: 8, padding: "6px 10px" };
const chipLabel = { display: "block", fontSize: 10, color: "var(--tg-theme-hint-color)", marginBottom: 2 };
const btnRow   = { display: "flex", gap: 8 };
const btnSuccess = { flex: 1, padding: "10px 0", borderRadius: 10, background: "var(--success)", color: "#fff", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 };
const btnDanger  = { flex: 1, padding: "10px 0", borderRadius: 10, background: "var(--danger)",  color: "#fff", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 };
