"use strict";
Object.defineProperties(exports, { __esModule: { value: true }, [Symbol.toStringTag]: { value: "Module" } });
const components = require("./components");
const coreExport = require("./core-export");
const installer = require("./installer");
Object.defineProperty(exports, "default", {
  enumerable: true,
  get: () => installer.installer
});
Object.keys(components).forEach((k) => {
  if (k !== "default" && !Object.prototype.hasOwnProperty.call(exports, k)) Object.defineProperty(exports, k, {
    enumerable: true,
    get: () => components[k]
  });
});
Object.keys(coreExport).forEach((k) => {
  if (k !== "default" && !Object.prototype.hasOwnProperty.call(exports, k)) Object.defineProperty(exports, k, {
    enumerable: true,
    get: () => coreExport[k]
  });
});
