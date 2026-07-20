// QA/QC portal (QA_QC). Backend: app/api/qaqc.py
PVW.registerPortal({
  id: "qaqc",
  label: "QA / QC",
  icon: "🔬",
  roles: ["QA_QC", "MANAGERIAL"],
  pages: [
    {
      id: "home",
      label: "Overview",
      render: function (el) { PVW.portalHome(el, "🔬 QA / QC",
        "FC grading, NCG items & dispositions, inspection, COA review.",
        "portal_qaqc.js", "/api/qaqc/ping"); },
    },
  ],
});
