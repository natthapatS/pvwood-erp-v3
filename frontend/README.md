# PVWood ERP v3 — Frontend

Vanilla ES-module SPA (no build step), served by FastAPI. **One file per portal**, so
you can build different portals in different terminals with zero merge conflicts.

## Layout
```
frontend/
  index.html              shell (login + sidebar + content); loads every script
  css/styles.css          shared styles (refine to the UX reference designs)
  js/
    api.js                PVW.api.get/post/... fetch wrapper + PVW.h() DOM helper
    i18n.js               PVW.t / PVW.addStrings
    nav.js                portal registry, sidebar, router, PVW.portalHome
    auth.js               placeholder login (role picker); real JWT lands with Admin
    app.js                bootstrap
    portals/
      portal_admin.js       ┐
      portal_planning.js    │
      portal_warehouse.js   │  one per portal — self-register via PVW.registerPortal(...)
      portal_production.js  │
      portal_qaqc.js        │
      portal_accounting.js  │
      portal_purchasing.js  ┘
```
Backend counterpart: `app/api/<portal>.py` (one router per portal, prefix `/api/<portal>`).

## Working on a portal (parallel terminals)
To build the **Warehouse** portal you touch only:
- `frontend/js/portals/portal_warehouse.js`  (UI: register pages)
- `app/api/warehouse.py`                      (endpoints under `/api/warehouse`)

Add a page:
```js
PVW.registerPortal({
  id: "warehouse", label: "Warehouse", icon: "📦",
  roles: ["WAREHOUSE", "MANAGERIAL"],
  pages: [
    { id: "lots", label: "RM Lots", render(el) {
        PVW.api.get("/api/warehouse/lots").then(rows => { /* build DOM into el */ });
    }},
  ],
});
```
`roles` drives RBAC (MANAGERIAL sees every portal). `PVW.h(tag, attrs, children)` is a
small DOM helper; `PVW.api` handles fetch + auth + JSON.

## Run
```
uvicorn app.main:app --reload --port 8001
```
Then open http://127.0.0.1:8001/ — pick a role to preview its portals.
