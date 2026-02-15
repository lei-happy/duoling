"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const components = require("./components");
function _interopNamespaceDefault(e) {
  const n = Object.create(null, { [Symbol.toStringTag]: { value: "Module" } });
  if (e) {
    for (const k in e) {
      if (k !== "default") {
        const d = Object.getOwnPropertyDescriptor(e, k);
        Object.defineProperty(n, k, d.get ? d : {
          enumerable: true,
          get: () => e[k]
        });
      }
    }
  }
  n.default = e;
  return Object.freeze(n);
}
const components__namespace = /* @__PURE__ */ _interopNamespaceDefault(components);
const installer = {
  install(app) {
    Object.keys(components__namespace).forEach((key) => {
      app.component(components__namespace[key].name, components__namespace[key]);
    });
  }
};
exports.installer = installer;
