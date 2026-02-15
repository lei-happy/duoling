"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const breadcrumbProps = {
  ...elementPlus.breadcrumbProps,
  separator: {
    type: [String, Object, Function],
    default: "/"
  },
  /** 面包屑数据 */
  items: {
    type: Array,
    required: true
  }
};
exports.breadcrumbProps = breadcrumbProps;
