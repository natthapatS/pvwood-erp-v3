// Placeholder auth (client-side role) until the Admin portal ships real login + JWT.
window.PVW = window.PVW || {};
PVW.ROLES = [
  "MANAGERIAL",
  "PRODUCTION_PLANNING",
  "WAREHOUSE",
  "DEPARTMENT_LEADER",
  "QA_QC",
  "ACCOUNTING",
  "PURCHASING",
];

PVW.login = function (role, name) {
  PVW.session = { role, name: name || role };
  localStorage.setItem("pvw_session", JSON.stringify(PVW.session));
  PVW.showApp();
};

PVW.logout = function () {
  PVW.session = null;
  localStorage.removeItem("pvw_session");
  PVW.showLogin();
};

PVW.restore = function () {
  try {
    const s = JSON.parse(localStorage.getItem("pvw_session"));
    if (s && s.role) { PVW.session = s; return true; }
  } catch (e) { /* ignore */ }
  return false;
};

PVW.showApp = function () {
  document.getElementById("login-view").hidden = true;
  document.getElementById("app-view").hidden = false;
  document.getElementById("user-label").textContent = PVW.session.name + " · " + PVW.session.role;
  PVW.renderSidebar();
};

PVW.showLogin = function () {
  document.getElementById("app-view").hidden = true;
  document.getElementById("login-view").hidden = false;
};
