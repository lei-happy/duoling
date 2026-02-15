"use strict";
Object.defineProperties(exports, { __esModule: { value: true }, [Symbol.toStringTag]: { value: "Module" } });
const coreComponents = require("./core-components");
const coreExport = require("./core-export");
const coreInstaller = require("./core-installer");
Object.defineProperty(exports, "default", {
  enumerable: true,
  get: () => coreInstaller.installer
});
Object.keys(coreComponents).forEach((k) => {
  if (k !== "default" && !Object.prototype.hasOwnProperty.call(exports, k)) Object.defineProperty(exports, k, {
    enumerable: true,
    get: () => coreComponents[k]
  });
});
Object.keys(coreExport).forEach((k) => {
  if (k !== "default" && !Object.prototype.hasOwnProperty.call(exports, k)) Object.defineProperty(exports, k, {
    enumerable: true,
    get: () => coreExport[k]
  });
});
