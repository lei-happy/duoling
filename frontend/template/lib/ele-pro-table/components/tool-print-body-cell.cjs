"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const util = require("../../ele-virtual-table/util");
const _hoisted_1 = ["colspan", "rowspan"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ToolPrintBodyCell" },
  __name: "tool-print-body-cell",
  props: {
    /** 列数据 */
    col: {
      type: Object,
      required: true
    },
    /** 列索引 */
    columnIndex: Number,
    /** 单元格样式 */
    bodyCellStyle: [Object, Function],
    /** 单元格类名自定义 */
    bodyCellClass: [String, Function]
  },
  setup(__props) {
    const props = __props;
    const slots = vue.useSlots();
    const renderOpt = vue.computed(() => {
      const { text, row, column, index: $index } = props.col;
      const params = [{ row, column, $index }];
      const slotName = column ? column.printSlot || column.slot : void 0;
      if (column && "expand" !== column.type && slotName && typeof slots[slotName] === "function") {
        return { render: slots[slotName], params };
      }
      return { render: () => text, params };
    });
    const cellParam = vue.computed(() => {
      return {
        column: props.col.column,
        columnIndex: props.columnIndex,
        rowIndex: props.col.index,
        row: props.col.row
      };
    });
    const cellStyle = vue.computed(() => {
      if (typeof props.bodyCellStyle === "function") {
        if (cellParam.value.column == null) {
          return;
        }
        return props.bodyCellStyle(cellParam.value);
      }
      return props.bodyCellStyle;
    });
    const cellClass = vue.computed(() => {
      const classes = [];
      const column = cellParam.value.column;
      if (column) {
        if (column.align) {
          classes.push(`is-align-${column.align}`);
        }
        if (typeof props.bodyCellClass === "function") {
          const temp = props.bodyCellClass(cellParam.value);
          if (temp) {
            classes.push(temp);
          }
        } else if (props.bodyCellClass) {
          classes.push(props.bodyCellClass);
        }
        if (column.className) {
          classes.push(column.className);
        }
      }
      return classes.join(" ");
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("td", {
        colspan: __props.col.colspan,
        rowspan: __props.col.rowspan,
        style: vue.normalizeStyle(cellStyle.value),
        class: vue.normalizeClass(cellClass.value)
      }, [
        "expand" === __props.col.column?.type ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
          __props.col.text != null && __props.col.text !== "" ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
            vue.createTextVNode(vue.toDisplayString(__props.col.text), 1)
          ], 64)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
            key: 1,
            style: { "vertical-align": "middle" },
            class: "ele-print-expand-icon"
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(index.ArrowDown))
            ]),
            _: 1
          }))
        ], 64)) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
          __props.col.isTreeCell ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
            __props.col.indent ? (vue.openBlock(), vue.createElementBlock("span", {
              key: 0,
              style: vue.normalizeStyle({ paddingLeft: `${__props.col.indent * 16}px` }),
              class: "ele-print-tree-indent"
            }, null, 4)) : vue.createCommentVNode("", true),
            vue.createVNode(vue.unref(elementPlus.ElIcon), {
              style: vue.normalizeStyle({
                verticalAlign: "middle",
                marginRight: "2px",
                visibility: __props.col.isTreeLeaf ? "hidden" : void 0
              }),
              class: "ele-print-tree-icon"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.ArrowDown))
              ]),
              _: 1
            }, 8, ["style"])
          ], 64)) : vue.createCommentVNode("", true),
          vue.createVNode(vue.unref(util.CellRender), vue.normalizeProps(vue.guardReactiveProps(renderOpt.value)), null, 16)
        ], 64))
      ], 14, _hoisted_1);
    };
  }
});
module.exports = _sfc_main;
