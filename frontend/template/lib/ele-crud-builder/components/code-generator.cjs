"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const codeUtil = require("../../ele-pro-form-builder/components/code-util");
const codeTemplate = require("./code-template");
function generateElCode(_data) {
  return "";
}
function generateProCode(data) {
  const config = JSON.parse(
    JSON.stringify({ ...data || {}, fields: data?.fields || [] })
  );
  const templateData = {
    proCrudConfigCode: codeUtil.obj2Str(config, false, 2, () => void 0)
  };
  return codeUtil.templateEngine(codeTemplate.proTemplate, templateData);
}
exports.generateElCode = generateElCode;
exports.generateProCode = generateProCode;
