"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const elementPlus = require("element-plus");
const error = require("element-plus/es/utils/error");
const SELECT_DATA_KEY = Symbol(
  "selectData"
);
function isEmptyValue(value, multiple) {
  if (value == null || value === "") {
    return true;
  }
  if (multiple && !value.length) {
    return true;
  }
  return false;
}
function valueIsChanged(value1, value2, multiple) {
  const isNull1 = isEmptyValue(value1);
  const isNull2 = isEmptyValue(value2);
  if (isNull1 && isNull2) {
    return false;
  }
  if (!multiple) {
    return isNull1 !== isNull2 || value1 !== value2;
  }
  const isEmpty1 = isNull1 || !value1.length;
  const isEmpty2 = isNull2 || !value2.length;
  if (isEmpty1 && isEmpty2) {
    return false;
  }
  if (isEmpty1 !== isEmpty2) {
    return true;
  }
  if (value1.length !== value2.length) {
    return true;
  }
  for (let i = 0; i < value1.length; i++) {
    if (value1[i] !== value2[i]) {
      return true;
    }
  }
  return false;
}
function useFormValidate() {
  const formItem = vue.inject(elementPlus.formItemContextKey, null);
  const validateChange = () => {
    if (formItem != null) {
      formItem.validate("change").catch((e) => error.debugWarn(e));
    }
  };
  return { validateChange };
}
exports.SELECT_DATA_KEY = SELECT_DATA_KEY;
exports.isEmptyValue = isEmptyValue;
exports.useFormValidate = useFormValidate;
exports.valueIsChanged = valueIsChanged;
