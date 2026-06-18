import { useState } from "react";
import ApplicationsPage  from "./ApplicationsPage";
import EmployeesPage     from "./EmployeesPage";
import DepartmentsPage   from "./DepartmentsPage";
import ReportPage        from "./ReportPage";
import DistributionPage  from "./DistributionPage";
import {
  IconClipboard, IconUsers, IconBuilding, IconBarChart, IconUtensilsCrossed,
} from "../../components/Icons";

const TABS = [
  { key: "applications", label: "Arizalar",  Icon: IconClipboard },
  { key: "employees",    label: "Hodimlar",  Icon: IconUsers },
  { key: "departments",  label: "Bo'limlar", Icon: IconBuilding },
  { key: "report",       label: "Hisobot",   Icon: IconBarChart },
  { key: "distribution", label: "Tarqatish", Icon: IconUtensilsCrossed },
];

export default function AdminApp() {
  const [active, setActive] = useState("applications");

  function renderPage() {
    switch (active) {
      case "applications":  return <ApplicationsPage />;
      case "employees":     return <EmployeesPage />;
      case "departments":   return <DepartmentsPage />;
      case "report":        return <ReportPage />;
      case "distribution":  return <DistributionPage />;
      default:              return null;
    }
  }

  return (
    <div style={root}>
      {/* Content */}
      <div style={content}>
        {renderPage()}
      </div>

      {/* Bottom nav */}
      <nav style={nav}>
        {TABS.map(({ key, label, Icon }) => {
          const isActive = active === key;
          return (
            <button
              key={key}
              style={tabBtn(isActive)}
              onClick={() => setActive(key)}
            >
              <Icon size={22} color={isActive ? "var(--accent)" : "var(--tg-theme-hint-color)"} />
              <span style={tabLabel(isActive)}>{label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}

const root    = { display: "flex", flexDirection: "column", height: "100dvh", background: "var(--tg-theme-bg-color)" };
const content = { flex: 1, overflowY: "auto", paddingBottom: 8 };
const nav     = {
  display: "flex",
  borderTop: "1px solid rgba(0,0,0,0.09)",
  background: "var(--tg-theme-bg-color)",
  paddingBottom: "env(safe-area-inset-bottom)",
};
const tabBtn = active => ({
  flex: 1,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  padding: "8px 2px 6px",
  background: "none",
  border: "none",
  cursor: "pointer",
  color: active ? "var(--accent)" : "var(--tg-theme-hint-color)",
});
const tabLabel = active => ({ fontSize: 10, marginTop: 3, fontWeight: active ? 700 : 400 });
