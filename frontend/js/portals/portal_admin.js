// Admin portal (MANAGERIAL). Backend: app/api/admin.py
PVW.registerPortal({
  id: "admin",
  label: "Admin",
  icon: "🛠️",
  roles: ["MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "🛠️ Admin",
        "Master data, enums, users, Factory Assistant, system config.",
        "portal_admin.js", "/api/admin/ping"); },
    },
  ],
});
