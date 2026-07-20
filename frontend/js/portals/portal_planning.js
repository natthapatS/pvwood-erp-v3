// Planning portal (PRODUCTION_PLANNING). Backend: app/api/planning.py
PVW.registerPortal({
  id: "planning",
  label: "Planning",
  icon: "🗓️",
  roles: ["PRODUCTION_PLANNING", "MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "🗓️ Planning",
        "Sales & production orders, BOM, scheduling, material shortfalls.",
        "portal_planning.js", "/api/planning/ping"); },
    },
  ],
});
