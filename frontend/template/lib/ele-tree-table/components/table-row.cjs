"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = { class: "ele-tree-table-row-body" };
const _hoisted_2 = { class: "ele-tree-table-cells" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "TableRow" },
  __name: "table-row",
  props: {
    /** 行索引 */
    rowIndex: {
      type: Number,
      required: true
    },
    /** 是否有子级 */
    hasChildren: Boolean,
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
    const isCollapse = vue.ref(false);
    const handleExpandClick = () => {
      isCollapse.value = !isCollapse.value;
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-tree-table-row", { "is-collapse": isCollapse.value }])
      }, [
        vue.createElementVNode("div", {
          style: vue.normalizeStyle({
            width: `${__props.indexColWidth}px`,
            left: `${(__props.level - 1) * __props.indexColWidth}px`
          }),
          class: vue.normalizeClass(["ele-tree-table-cell is-tree-index is-fixed-left", { "is-fixed-left-last": __props.depth === __props.level }])
        }, vue.toDisplayString(__props.rowIndex + 1), 7),
        vue.createElementVNode("div", _hoisted_1, [
          vue.createElementVNode("div", _hoisted_2, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.depth - __props.level, (num) => {
              return vue.openBlock(), vue.createElementBlock("div", {
                key: num,
                style: vue.normalizeStyle({
                  width: `${__props.indexColWidth}px`,
                  left: `${(__props.level - 1 + num) * __props.indexColWidth}px`,
                  textAlign: __props.hasChildren && num === 1 ? "left" : void 0
                }),
                class: vue.normalizeClass(["ele-tree-table-cell is-tree-index is-placeholder is-fixed-left", { "is-fixed-left-last": num === __props.depth - __props.level }])
              }, [
                __props.hasChildren && num === 1 ? (vue.openBlock(), vue.createElementBlock("div", {
                  key: 0,
                  class: vue.normalizeClass(["ele-tree-table-expand", { "is-collapse": isCollapse.value }]),
                  onClick: handleExpandClick
                }, [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.ArrowDown))
                    ]),
                    _: 1
                  })
                ], 2)) : vue.createCommentVNode("", true)
              ], 6);
            }), 128)),
            vue.renderSlot(_ctx.$slots, "cells")
          ]),
          vue.renderSlot(_ctx.$slots, "default")
        ])
      ], 2);
    };
  }
});
module.exports = _sfc_main;
