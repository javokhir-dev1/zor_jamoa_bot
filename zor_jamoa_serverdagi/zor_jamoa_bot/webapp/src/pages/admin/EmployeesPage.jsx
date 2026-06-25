import { useEffect, useState } from "react";
import { getUsers, addUser, updateUser, deleteUser, getAdminDepts } from "../../api/admin";
import { IconTrash, IconPlus, IconPhone, IconUser, IconShield, IconCheck } from "../../components/Icons";
import { PageLoader } from "../../components/Spinner";

export default function EmployeesPage() {
  const [users, setUsers]     = useState([]);
  const [depts, setDepts]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch]   = useState("");
  const [modal, setModal]     = useState(null);

  const load = () => {
    setLoading(true);
    Promise.all([getUsers({ status: "approved" }), getAdminDepts()])
      .then(([u, d]) => { setUsers(u); setDepts(d); })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = users.filter(u =>
    u.full_name.toLowerCase().includes(search.toLowerCase()) ||
    (u.phone_number || "").includes(search)
  );

  async function handleDelete(id) {
    if (!window.confirm("Hodimni tizimdan chiqarishni tasdiqlaysizmi?")) return;
    await deleteUser(id);
    load();
  }

  async function handleDeptChange(id, dept_id) {
    await updateUser(id, { department_id: dept_id ? parseInt(dept_id) : null });
    load();
  }

  async function handleRoleToggle(u) {
    const next = u.role === "admin" ? "employee" : "admin";
    const label = next === "admin" ? "admin qilish" : "hodimga qaytarish";
    if (!window.confirm(`${u.full_name}ni ${label}ni tasdiqlaysizmi?`)) return;
    await updateUser(u.id, { role: next });
    load();
  }

  function RoleIcon({ role }) {
    if (role === "admin")     return <IconShield size={13} color="var(--accent)" />;
    if (role === "dept_head") return <IconUser size={13} color="var(--warning)" />;
    return <IconUser size={13} color="var(--tg-theme-hint-color)" />;
  }

  return (
    <div style={page}>
      <div style={topRow}>
        <div style={titleRow}>
          <span style={titleText}>Hodimlar</span>
          <span style={count}>{users.length}</span>
        </div>
        <button style={btnAdd} onClick={() => setModal("add")} title="Qo'shish">
          <IconPlus size={18} color="#fff" />
        </button>
      </div>

      <div style={searchWrap}>
        <IconSearch16 />
        <input
          style={searchInput}
          placeholder="Ism yoki telefon..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? <PageLoader /> : filtered.length === 0 ? <Empty text="Hodim topilmadi" /> : (
        filtered.map(u => (
          <div key={u.id} style={card}>
            <div style={cardRow}>
              <div style={avatar}>{u.full_name[0]}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={name}>{u.full_name}</div>
                <div style={metaRow}>
                  <IconPhone size={12} color="var(--tg-theme-hint-color)" />
                  <span style={metaText}>{u.phone_number || "—"}</span>
                </div>
                <div style={metaRow}>
                  <RoleIcon role={u.role} />
                  <span style={metaText}>{roleLabel(u.role)}</span>
                </div>
              </div>
              <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                <button
                  style={u.role === "admin" ? btnAdminActive : btnAdminInactive}
                  onClick={() => handleRoleToggle(u)}
                  title={u.role === "admin" ? "Admin rolini olib tashlash" : "Admin qilish"}
                >
                  <IconShield size={15} color={u.role === "admin" ? "#fff" : "var(--accent)"} />
                </button>
                <button style={btnDanger} onClick={() => handleDelete(u.id)} title="O'chirish">
                  <IconTrash size={15} color="#fff" />
                </button>
              </div>
            </div>
            <select
              style={selectStyle}
              value={u.department_id || ""}
              onChange={e => handleDeptChange(u.id, e.target.value)}
            >
              <option value="">— Bo'limsiz —</option>
              {depts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
        ))
      )}

      {modal === "add" && (
        <AddUserModal depts={depts} onClose={() => setModal(null)} onSaved={load} />
      )}
    </div>
  );
}

function AddUserModal({ depts, onClose, onSaved }) {
  const [form, setForm]     = useState({ telegram_id: "", full_name: "", phone_number: "", department_id: "" });
  const [err, setErr]       = useState("");
  const [saving, setSaving] = useState(false);

  async function submit() {
    if (!form.telegram_id || !form.full_name) { setErr("Telegram ID va ism majburiy"); return; }
    setSaving(true);
    try {
      await addUser({
        telegram_id: parseInt(form.telegram_id),
        full_name: form.full_name,
        phone_number: form.phone_number || null,
        department_id: form.department_id ? parseInt(form.department_id) : null,
      });
      onSaved(); onClose();
    } catch (e) {
      setErr(e?.response?.data?.detail || "Xatolik");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={overlay}>
      <div style={modalBox}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <IconPlus size={18} color="var(--accent)" />
          <span style={{ fontWeight: 700, fontSize: 16 }}>Hodim qo'shish</span>
        </div>
        {err && <div style={errBox}>{err}</div>}
        <input style={inp} placeholder="Telegram ID *"   value={form.telegram_id}   onChange={e => setForm({ ...form, telegram_id: e.target.value })} />
        <input style={inp} placeholder="Ism-familiya *"   value={form.full_name}     onChange={e => setForm({ ...form, full_name: e.target.value })} />
        <input style={inp} placeholder="Telefon raqami"   value={form.phone_number}  onChange={e => setForm({ ...form, phone_number: e.target.value })} />
        <select style={inp} value={form.department_id} onChange={e => setForm({ ...form, department_id: e.target.value })}>
          <option value="">— Bo'lim tanlang —</option>
          {depts.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
          <button style={btnSave} onClick={submit} disabled={saving}>
            {saving ? <Spinner16 /> : <IconCheck size={16} color="#fff" />}
            {saving ? "Saqlanmoqda..." : "Saqlash"}
          </button>
          <button style={btnGray} onClick={onClose}>Bekor</button>
        </div>
      </div>
    </div>
  );
}

function IconSearch16() {
  return (
    <svg style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}
      width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--tg-theme-hint-color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function Spinner16() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"
      style={{ animation: "spin 0.8s linear infinite" }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  );
}

function roleLabel(r) { return { employee: "Hodim", dept_head: "Bo'lim rahbari", admin: "Admin" }[r] || r; }

const page     = { padding: "16px 14px", maxWidth: 520, margin: "0 auto" };
const topRow   = { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 };
const titleRow = { display: "flex", alignItems: "center", gap: 8 };
const titleText = { fontSize: 18, fontWeight: 700 };
const count    = { background: "var(--tg-theme-secondary-bg-color)", borderRadius: 12, padding: "2px 10px", fontSize: 13, fontWeight: 600 };
const btnAdd   = { width: 36, height: 36, borderRadius: 10, background: "var(--accent)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const searchWrap = { position: "relative", marginBottom: 12 };
const searchInput = { width: "100%", padding: "10px 14px 10px 36px", borderRadius: 10, border: "none", background: "var(--tg-theme-secondary-bg-color)", fontSize: 14, outline: "none" };
const card     = { background: "var(--tg-theme-secondary-bg-color)", borderRadius: 12, padding: "12px 14px", marginBottom: 8 };
const cardRow  = { display: "flex", alignItems: "flex-start", gap: 10, marginBottom: 10 };
const avatar   = { width: 38, height: 38, borderRadius: 19, background: "var(--accent)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 17, flexShrink: 0 };
const name     = { fontWeight: 700, fontSize: 14, marginBottom: 3 };
const metaRow  = { display: "flex", alignItems: "center", gap: 4, marginTop: 2 };
const metaText = { fontSize: 12, color: "var(--tg-theme-hint-color)" };
const selectStyle = { width: "100%", padding: "8px 10px", borderRadius: 8, border: "none", background: "var(--tg-theme-bg-color)", fontSize: 13 };
const btnDanger      = { width: 34, height: 34, borderRadius: 8, background: "var(--danger)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const btnAdminActive  = { width: 34, height: 34, borderRadius: 8, background: "var(--accent)", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const btnAdminInactive = { width: 34, height: 34, borderRadius: 8, background: "rgba(0,122,255,0.1)", border: "1.5px solid var(--accent)", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const btnSave  = { flex: 1, padding: "11px 0", borderRadius: 10, background: "var(--accent)", color: "#fff", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 };
const btnGray  = { flex: 1, padding: "11px 0", borderRadius: 10, background: "var(--tg-theme-secondary-bg-color)", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer" };
const overlay  = { position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "flex-end", zIndex: 100 };
const modalBox = { background: "var(--tg-theme-bg-color)", borderRadius: "16px 16px 0 0", padding: "20px 16px", width: "100%", maxHeight: "90vh", overflowY: "auto" };
const inp      = { display: "block", width: "100%", padding: "11px 14px", borderRadius: 10, border: "none", background: "var(--tg-theme-secondary-bg-color)", fontSize: 14, marginBottom: 10, outline: "none" };
const errBox   = { background: "rgba(229,57,53,0.1)", color: "var(--danger)", borderRadius: 8, padding: "8px 12px", fontSize: 13, marginBottom: 10 };
function Empty({ text }) { return <div style={{ textAlign: "center", padding: 40, color: "var(--tg-theme-hint-color)" }}>{text}</div>; }
