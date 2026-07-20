// Warehouse portal (WAREHOUSE). Backend: app/api/warehouse.py
PVW.registerPortal({
  id: "warehouse",
  label: "Warehouse",
  icon: "📦",
  roles: ["WAREHOUSE", "MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "📦 Warehouse",
        "RM lots, goods receipt, FG lots, locations, mobile scan.",
        "portal_warehouse.js", "/api/warehouse/ping"); },
    },
  ],
});
