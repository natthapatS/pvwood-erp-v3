// Purchasing portal (PURCHASING). Backend: app/api/purchasing.py
PVW.registerPortal({
  id: "purchasing",
  label: "Purchasing",
  icon: "🛒",
  roles: ["PURCHASING", "MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "🛒 Purchasing",
        "Suppliers, purchase orders, PO lines, receiving status.",
        "portal_purchasing.js", "/api/purchasing/ping"); },
    },
  ],
});
