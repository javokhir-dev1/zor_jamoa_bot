import { useEffect, useState } from "react";
import { useTelegram } from "./hooks/useTelegram";
import OrderPage     from "./pages/OrderPage";
import DeptHeadPage  from "./pages/DeptHeadPage";
import ClosedPage    from "./pages/ClosedPage";
import AdminApp      from "./pages/admin/AdminApp";
import { Spinner }   from "./components/Spinner";
import { IconLock }  from "./components/Icons";

// Toshkent vaqti bo'yicha buyurtma ochiqmi?
function isOrderOpen() {
  const now = new Date();
  const tashkent = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Tashkent" }));
  const h = tashkent.getHours();
  const m = tashkent.getMinutes();
  const totalMinutes = h * 60 + m;
  // 00:00 dan 13:55 gacha ochiq
  return totalMinutes < 13 * 60 + 55;
}

const IS_ADMIN_ROUTE = window.location.pathname.startsWith("/admin");

export default function App() {
  const { ready, expand, tg } = useTelegram();
  const [view, setView] = useState("loading"); // "loading" | "closed" | "order" | "dept_head" | "admin" | "forbidden" | "register_needed"

  useEffect(() => {
    ready();
    expand();

    // Telegram theme ranglarini CSS ga ulash
    if (tg?.themeParams) {
      const p = tg.themeParams;
      const root = document.documentElement.style;
      if (p.bg_color)           root.setProperty("--tg-theme-bg-color", p.bg_color);
      if (p.text_color)         root.setProperty("--tg-theme-text-color", p.text_color);
      if (p.hint_color)         root.setProperty("--tg-theme-hint-color", p.hint_color);
      if (p.link_color)         root.setProperty("--tg-theme-link-color", p.link_color);
      if (p.button_color)       root.setProperty("--tg-theme-button-color", p.button_color);
      if (p.button_text_color)  root.setProperty("--tg-theme-button-text-color", p.button_text_color);
      if (p.secondary_bg_color) root.setProperty("--tg-theme-secondary-bg-color", p.secondary_bg_color);
    }

    if (IS_ADMIN_ROUTE) {
      detectAdminView();
    } else {
      // Oddiy foydalanuvchi — vaqt tekshiruvi
      if (!isOrderOpen()) {
        setView("closed");
        return;
      }
      detectUserView();
    }
  }, []);

  // /admin yo'lida: admin ekanligini tekshir
  async function detectAdminView() {
    try {
      const { default: client } = await import("./api/client");
      await client.get("/admin/applications");
      setView("admin");
    } catch (e) {
      setView("forbidden");
    }
  }

  // / yo'lida: dept_head yoki oddiy hodim
  async function detectUserView() {
    try {
      const { default: client } = await import("./api/client");
      try {
        await client.get("/departments/my-dept/members");
        setView("dept_head");
      } catch (e) {
        setView("order");
      }
    } catch {
      setView("order");
    }
  }

  if (view === "loading") {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 16 }}>
        <Spinner size={40} />
        <p style={{ color: "var(--tg-theme-hint-color)", fontSize: 14 }}>Yuklanmoqda...</p>
      </div>
    );
  }

  if (view === "forbidden") {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 14, padding: 24 }}>
        <div style={{ width: 64, height: 64, borderRadius: 32, background: "rgba(229,57,53,0.1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <IconLock size={30} color="var(--danger)" />
        </div>
        <p style={{ fontWeight: 700, fontSize: 18 }}>Kirish taqiqlangan</p>
        <p style={{ color: "var(--tg-theme-hint-color)", textAlign: "center", fontSize: 14 }}>Bu sahifa faqat adminlar uchun.</p>
      </div>
    );
  }

  if (view === "closed") return <ClosedPage />;
  if (view === "admin") return <AdminApp />;
  if (view === "dept_head") return <DeptHeadTabs />;
  return <OrderPage />;
}

// Bo'lim rahbari uchun tab navigatsiya
function DeptHeadTabs() {
  const [tab, setTab] = useState("self"); // "self" | "dept"

  return (
    <div>
      {/* Tab bar */}
      <div
        style={{
          display: "flex",
          borderBottom: "2px solid var(--tg-theme-secondary-bg-color)",
          position: "sticky",
          top: 0,
          background: "var(--tg-theme-bg-color)",
          zIndex: 10,
        }}
      >
        {[
          { key: "self", label: "👤 O'zim uchun" },
          { key: "dept", label: "👥 Bo'lim uchun" },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            style={{
              flex: 1,
              padding: "14px 8px",
              background: "transparent",
              fontWeight: tab === t.key ? 700 : 400,
              fontSize: 14,
              color:
                tab === t.key
                  ? "var(--accent)"
                  : "var(--tg-theme-hint-color)",
              borderBottom:
                tab === t.key
                  ? "2px solid var(--accent)"
                  : "2px solid transparent",
              marginBottom: -2,
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "self" ? <OrderPage /> : <DeptHeadPage />}
    </div>
  );
}
