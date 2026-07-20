// Minimal i18n. Portals add keys: PVW.addStrings('warehouse', { en:{...}, th:{...}, zh:{...} })
window.PVW = window.PVW || {};
PVW.lang = localStorage.getItem("pvw_lang") || "en";
PVW.i18n = { en: {}, th: {}, zh: {} };

PVW.addStrings = function (ns, byLang) {
  for (const lang in byLang) {
    PVW.i18n[lang] = PVW.i18n[lang] || {};
    for (const k in byLang[lang]) PVW.i18n[lang][ns + "." + k] = byLang[lang][k];
  }
};

PVW.t = function (key) {
  const d = PVW.i18n[PVW.lang] || {};
  return d[key] != null ? d[key] : key;
};

PVW.setLang = function (lang) {
  PVW.lang = lang;
  localStorage.setItem("pvw_lang", lang);
};
