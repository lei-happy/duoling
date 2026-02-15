"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const props = require("../ele-data-table/props");
const virtualTableProps = {
  ...props.dataTableProps,
  /** 行高 */
  rowHeight: Number
};
const virtualTableEmits = {
  ...props.dataTableEmits,
  endEeached: (_params) => true,
  scroll: (_params) => true,
  rowsRendered: (_params) => true
};
exports.virtualTableEmits = virtualTableEmits;
exports.virtualTableProps = virtualTableProps;
