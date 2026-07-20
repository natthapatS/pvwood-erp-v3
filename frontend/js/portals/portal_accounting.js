// Accounting portal (ACCOUNTING). Backend: app/api/accounting.py
PVW.registerPortal({
  id: "accounting",
  label: "Accounting",
  icon: "💰",
  roles: ["ACCOUNTING", "MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "💰 Accounting",
        "TAS 2 per-batch costing, cost ledgers, financial reports.",
        "portal_accounting.js", "/api/accounting/ping"); },
    },
  ],
});
