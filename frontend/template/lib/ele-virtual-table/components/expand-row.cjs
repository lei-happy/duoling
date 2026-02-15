"use strict";
const vue = require("vue");
const _hoisted_1 = { class: "el-table-v2__row-cell ele-table-td" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ExpandRow" },
  __name: "expand-row",
  props: {
    /** 列配置(原始配置) */
    column: Object,
    /** 行索引 */
    rowIndex: Number,
    /** 行数据(原始数据) */
    rowData: Object
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        __props.column && __props.column.slot ? vue.renderSlot(_ctx.$slots, __props.column.slot, vue.normalizeProps(vue.mergeProps({ key: 0 }, { row: __props.rowData, column: __props.column, $index: __props.rowIndex }))) : vue.createCommentVNode("", true)
      ]);
    };
  }
});
module.exports = _sfc_main;
