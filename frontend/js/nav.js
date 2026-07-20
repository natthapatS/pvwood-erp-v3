// Portal registry + sidebar + router. Portal files call PVW.registerPortal(...).
window.PVW = window.PVW || {};
PVW.portals = [];

// def = { id, label, icon?, roles:[...], pages:[{ id, label, render(el) }] }
PVW.registerPortal = function (def) { PVW.portals.push(def); };

PVW.visiblePortals = function () {
  const role = PVW.session && PVW.session.role;
  return PVW.portals.filter((p) => p.roles.includes(role));
};

PVW.renderSidebar = function () {
  const portals = PVW.visiblePortals();
  const sb = document.getElementById("sidebar");
  sb.innerHTML =
    '<div class="brand">PVWood ERP</div>' +
    portals
      .map(
        (p) =>
          '<div class="portal-group"><div class="portal-label">' +
          (p.icon ? p.icon + " " : "") + p.label + "</div>" +
          p.pages
            .map((pg) => '<a class="nav-link" data-page="' + p.id + "." + pg.id + '">' + pg.label + "</a>")
            .join("") +
          "</div>"
      )
      .join("");
  sb.querySelectorAll(".nav-link").forEach((a) => (a.onclick = () => PVW.navigateTo(a.dataset.page)));
  const first = portals[0] && portals[0].pages[0];
  if (first) PVW.navigateTo(portals[0].id + "." + first.id);
};

// Shared scaffold landing page for a portal (description + live API ping).
PVW.portalHome = function (el, title, desc, file, pingPath) {
  const py = file.replace("portal_", "").replace(".js", ".py");
  el.appendChild(
    PVW.h("div", { class: "card" }, [
      PVW.h("h2", {}, title),
      PVW.h("p", { class: "muted" }, desc),
      PVW.h("p", { class: "muted" }, "Build pages in frontend/js/portals/" + file + " + app/api/" + py + "."),
    ])
  );
  const s = PVW.h("div", { class: "muted" }, "checking API…");
  el.appendChild(s);
  PVW.api
    .get(pingPath)
    .then(function (r) { s.className = "ok"; s.textContent = "API OK: " + JSON.stringify(r); })
    .catch(function (e) { s.className = "error"; s.textContent = "API error: " + e.message; });
};

PVW.navigateTo = function (key) {
  const [pid, pgid] = key.split(".");
  const portal = PVW.portals.find((p) => p.id === pid);
  const page = portal && portal.pages.find((pg) => pg.id === pgid);
  const content = document.getElementById("content");
  document.getElementById("page-title").textContent = portal && page ? portal.label + " · " + page.label : "";
  document.querySelectorAll(".nav-link").forEach((a) => a.classList.toggle("active", a.dataset.page === key));
  document.getElementById("sidebar").classList.remove("open");
  content.innerHTML = "";
  if (!page) { content.innerHTML = '<div class="empty">Page not found</div>'; return; }
  try {
    Promise.resolve(page.render(content)).catch((e) => (content.innerHTML = '<div class="error">' + e.message + "</div>"));
  } catch (e) {
    content.innerHTML = '<div class="error">' + e.message + "</div>";
  }
};
