// Bootstrap: wire the login form + top bar, restore any session.
document.addEventListener("DOMContentLoaded", function () {
  const sel = document.getElementById("role-select");
  sel.innerHTML = PVW.ROLES.map((r) => '<option value="' + r + '">' + r + "</option>").join("");

  document.getElementById("login-btn").onclick = function () {
    PVW.login(sel.value, document.getElementById("name-input").value.trim());
  };
  document.getElementById("name-input").addEventListener("keydown", function (e) {
    if (e.key === "Enter") document.getElementById("login-btn").click();
  });
  document.getElementById("logout-btn").onclick = function () { PVW.logout(); };
  document.getElementById("menu-btn").onclick = function () {
    document.getElementById("sidebar").classList.toggle("open");
  };

  if (PVW.restore()) PVW.showApp();
  else PVW.showLogin();
});
