"use strict";
const vue = require("vue");
const TableRow = require("./table-row");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "TableBody" },
  __name: "table-body",
  props: {
    /** 数据 */
    data: {
      type: Array,
      required: true
    },
    /** 列配置 */
    columns: {
      type: Array,
      required: true
    },
    /** 序号列宽度 */
    indexColWidth: {
      type: Number,
      required: true
    },
    /** 所处深度 */
    level: {
      type: Number,
      required: true
    },
    /** 最大深度 */
    depth: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      const _component_TableBody = vue.resolveComponent("TableBody", true);
      return vue.openBlock(), vue.createElementBlock("div", null, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.data, (row, rowIndex) => {
          return vue.openBlock(), vue.createBlock(TableRow, {
            key: row.key ?? rowIndex,
            rowIndex,
            hasChildren: !!(row.children && row.children.length),
            indexColWidth: __props.indexColWidth,
            level: __props.level,
            depth: __props.depth
          }, {
            cells: vue.withCtx(() => [
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.columns, (col) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: col.key ?? col.prop,
                  style: vue.normalizeStyle(col.style),
                  class: vue.normalizeClass([col.class, "ele-tree-table-cell"])
                }, [
                  vue.renderSlot(_ctx.$slots, "bodyCell", {
                    row,
                    rowIndex,
                    column: col,
                    treeLevel: __props.level
                  }, () => [
                    vue.createTextVNode(vue.toDisplayString(col.prop != null ? row[col.prop] : void 0), 1)
                  ])
                ], 6);
              }), 128))
            ]),
            default: vue.withCtx(() => [
              row.children && row.children.length ? (vue.openBlock(), vue.createBlock(_component_TableBody, {
                key: 0,
                data: row.children,
                columns: __props.columns,
                level: __props.level + 1,
                depth: __props.depth,
                indexColWidth: __props.indexColWidth,
                class: "ele-tree-table-children"
              }, vue.createSlots({ _: 2 }, [
                vue.renderList(Object.keys(_ctx.$slots), (name) => {
                  return {
                    name,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, name, vue.mergeProps({ ref_for: true }, slotProps || {}))
                    ])
                  };
                })
              ]), 1032, ["data", "columns", "level", "depth", "indexColWidth"])) : vue.createCommentVNode("", true)
            ]),
            _: 2
          }, 1032, ["rowIndex", "hasChildren", "indexColWidth", "level", "depth"]);
        }), 128))
      ]);
    };
  }
});
module.exports = _sfc_main;
