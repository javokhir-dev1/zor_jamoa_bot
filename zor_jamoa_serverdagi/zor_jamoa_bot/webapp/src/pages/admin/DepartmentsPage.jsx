import { useEffect, useState } from "react";
import {
  getAdminDepts, addDepartment, editDepartment, deleteDepartment,
  setDeptHead, getDeptMembers,
} from "../../api/admin";
import { IconEdit, IconTrash, IconCrown, IconPlus, IconBuilding, IconUser, IconCheck } from "../../components/Icons";
import { PageLoader } from "../../components/Spinner";

export default function DepartmentsPage() {
  const [depts, setDepts]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal]     = useState(null); // null | "add" | {type:"edit"|"head", dept}

  const load = () => {
    setLoading(true);
    getAdminDepts().then(setDepts).finally(() => setLoading(false));
  };

  useEffect(load, []);

  async function handleDelete(d) {
    if (!window.confirm(`"${d.name}" bo'limini o'chirishni tasdiqlaysizmi?`)) return;
    await deleteDepartment(d.id);
    load();
  }

  return (
    <div style={page}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <IconBuilding size={20} color="var(--accent)" />
          <span style={title}>Bo'limlar</span>
          <span style={countBadge}>{depts.length}</span>
        </div>
        <button style={btnPrimary} onClick={() => setModal("add")}>
          <IconPlus size={16} color="#fff" />
        </button>
      </div>

      {loading ? <Loader /> : depts.length === 0 ? <Empty text="Bo'lim yo'q" /> : (
        depts.map(d => (
          <div key={d.id} style={card}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15 }}>{d.name}</div>
                <div style={meta}>
                <IconUser size={12} color="var(--tg-theme-hint-color)" />
                {" "}{d.head_full_name || "Rahbar yo'q"}
              </div>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <button style={btnIcon} onClick={() => setModal({ type: "head", dept: d })} title="Rahbar belgilash">
                  <IconCrown size={16} color="#fff" />
                </button>
                <button style={btnIcon} onClick={() => setModal({ type: "edit", dept: d })} title="Tahrirlash">
                  <IconEdit size={16} color="#fff" />
                </button>
                <button style={{ ...btnIcon, background: "var(--danger)" }} onClick={() => handleDelete(d)} title="O'chirish">
                  <IconTrash size={16} color="#fff" />
                </button>
              </div>
            </div>
          </div>
        ))
      )}

      {modal === "add" && (
        <AddDeptModal onClose={() => setModal(null)} onSaved={load} />
      )}
      {modal?.type === "edit" && (
        <EditDeptModal dept={modal.dept} onClose={() => setModal(null)} onSaved={load} />
      )}
      {modal?.type === "head" && (
        <SetHeadModal dept={modal.dept} onClose={() => setModal(null)} onSaved={load} />
      )}
    </div>
  );
}

function AddDeptModal({ onClose, onSaved }) {
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit() {
    if (!name.trim()) return;
    setSaving(true);
    await addDepartment(name.trim());
    onSaved(); onClose();
  }

  return (
    <BottomModal title="➕ Bo'lim qo'shish" onClose={onClose}>
      <input style={inp} placeholder="Bo'lim nomi *" value={name} onChange={e => setName(e.target.value)} autoFocus />
      <div style={{ display: "flex", gap: 8 }}>
        <button style={{ ...btnPrimary, flex: 1 }} onClick={submit} disabled={saving || !name.trim()}>
          {saving ? "⏳..." : "✅ Saqlash"}
        </button>
        <button style={{ ...btnGray, flex: 1 }} onClick={onClose}>Bekor</button>
      </div>
    </BottomModal>
  );
}

function EditDeptModal({ dept, onClose, onSaved }) {
  const [name, setName] = useState(dept.name);
  const [saving, setSaving] = useState(false);

  async function submit() {
    if (!name.trim() || name.trim() === dept.name) { onClose(); return; }
    setSaving(true);
    await editDepartment(dept.id, name.trim());
    onSaved(); onClose();
  }

  return (
    <BottomModal title={`✏️ Tahrirlash: ${dept.name}`} onClose={onClose}>
      <input style={inp} value={name} onChange={e => setName(e.target.value)} autoFocus />
      <div style={{ display: "flex", gap: 8 }}>
        <button style={{ ...btnPrimary, flex: 1 }} onClick={submit} disabled={saving}>
          {saving ? "⏳..." : "✅ Saqlash"}
        </button>
        <button style={{ ...btnGray, flex: 1 }} onClick={onClose}>Bekor</button>
      </div>
    </BottomModal>
  );
}

function SetHeadModal({ dept, onClose, onSaved }) {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(dept.head_user_id || "");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getDeptMembers(dept.id).then(setMembers).finally(() => setLoading(false));
  }, [dept.id]);

  async function submit() {
    setSaving(true);
    await setDeptHead(dept.id, selected ? parseInt(selected) : null);
    onSaved(); onClose();
  }

  return (
    <BottomModal title={`👑 Rahbar: ${dept.name}`} onClose={onClose}>
      {loading ? <Loader /> : (
        <>
          <select style={{ ...inp }} value={selected} onChange={e => setSelected(e.target.value)}>
            <option value="">— Rahbar yo'q —</option>
            {members.map(m => <option key={m.id} value={m.id}>{m.full_name}</option>)}
          </select>
          <div style={{ display: "flex", gap: 8 }}>
            <button style={{ ...btnPrimary, flex: 1 }} onClick={submit} disabled={saving}>
              {saving ? "⏳..." : "✅ Saqlash"}
            </button>
            <button style={{ ...btnGray, flex: 1 }} onClick={onClose}>Bekor</button>
          </div>
        </>
      )}
    </BottomModal>
  );
}

function BottomModal({ title, onClose, children }) {
  return (
    <div style={overlay}>
      <div style={modalBox}>
        <h3 style={{ marginBottom: 16, fontSize: 16 }}>{title}</h3>
        {children}
      </div>
    </div>
  );
}

const page = { padding: "16px 14px", maxWidth: 520, margin: "0 auto" };
const title = { fontSize: 18, fontWeight: 700 };
const countBadge = { background: "var(--tg-theme-secondary-bg-color)", borderRadius: 12, padding: "2px 10px", fontSize: 13, fontWeight: 600 };
const card = { background: "var(--tg-theme-secondary-bg-color)", borderRadius: 12, padding: "12px 14px", marginBottom: 8 };
const meta = { fontSize: 12, color: "var(--tg-theme-hint-color)", marginTop: 3 };
const btnPrimary = { padding: "9px 14px", borderRadius: 10, background: "var(--accent)", color: "#fff", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const btnGray    = { padding: "10px 16px", borderRadius: 10, background: "var(--tg-theme-secondary-bg-color)", fontWeight: 600, fontSize: 13, border: "none", cursor: "pointer" };
const btnIcon    = { padding: "7px 10px", borderRadius: 8, background: "var(--tg-theme-hint-color)", color: "#fff", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" };
const overlay    = { position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "flex-end", zIndex: 100 };
const modalBox   = { background: "var(--tg-theme-bg-color)", borderRadius: "16px 16px 0 0", padding: "20px 16px", width: "100%", maxHeight: "80vh", overflowY: "auto" };
const inp = { display: "block", width: "100%", padding: "11px 14px", borderRadius: 10, border: "1.5px solid var(--tg-theme-secondary-bg-color)", background: "var(--tg-theme-secondary-bg-color)", fontSize: 14, marginBottom: 12, outline: "none" };
function Loader() { return <PageLoader />; }
function Empty({ text }) { return <div style={{ textAlign: "center", padding: 40, color: "var(--tg-theme-hint-color)" }}>{text}</div>; }
