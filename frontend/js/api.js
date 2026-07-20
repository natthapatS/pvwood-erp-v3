// Shared fetch wrapper. Usage: PVW.api.get('/api/warehouse/lots')
window.PVW = window.PVW || {};
PVW.api = {
  async req(method, path, body) {
    const opts = { method, headers: {} };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    const tok = PVW.session && PVW.session.token;
    if (tok) opts.headers["Authorization"] = "Bearer " + tok;
    const res = await fetch(path, opts);
    if (!res.ok) {
      let msg;
      try { msg = (await res.json()).detail; } catch (e) { msg = res.statusText; }
      throw new Error(msg || "HTTP " + res.status);
    }
    const ct = res.headers.get("content-type") || "";
    return ct.includes("application/json") ? res.json() : res.text();
  },
  get(p) { return this.req("GET", p); },
  post(p, b) { return this.req("POST", p, b); },
  put(p, b) { return this.req("PUT", p, b); },
  del(p) { return this.req("DELETE", p); },
};

// Tiny DOM helper for portals: PVW.h('div', {class:'card'}, 'text' | [nodes])
PVW.h = function (tag, attrs, children) {
  const el = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === "class") el.className = attrs[k];
    else if (k.startsWith("on") && typeof attrs[k] === "function") el.addEventListener(k.slice(2), attrs[k]);
    else if (attrs[k] != null) el.setAttribute(k, attrs[k]);
  }
  (Array.isArray(children) ? children : children != null ? [children] : []).forEach((c) =>
    el.appendChild(typeof c === "string" ? document.createTextNode(c) : c)
  );
  return el;
};
