// Production portal (DEPARTMENT_LEADER). Backend: app/api/production.py
PVW.registerPortal({
  id: "production",
  label: "Production",
  icon: "🏭",
  roles: ["DEPARTMENT_LEADER", "MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "🏭 Production",
        "Kanban board, station logs, batch flow across every line.",
        "portal_production.js", "/api/production/ping"); },
    },
  ],
});
