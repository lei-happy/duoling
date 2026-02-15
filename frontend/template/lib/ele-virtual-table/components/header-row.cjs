"use strict";
const vue = require("vue");
const util = require("../util");
const HeaderCell = require("./header-cell");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "HeaderRow" },
  __name: "header-row",
  props: {
    /** 表头行配置 */
    headerCols: Array,
    /** 表头所有行列宽 */
    headerColSizes: Array,
    /** 当前行索引 */
    headerIndex: Number,
    /** 表格排序状态 */
    sortBy: Object,
    /** 表格筛选值 */
    filtered: Object,
    /** 表格是否是全选状态 */
    isCheckAll: Boolean,
    /** 表格是否是半选状态 */
    isIndeterminate: Boolean,
    /** 是否禁用表头选择框 */
    disabledCheckbox: Boolean,
    /** 表格尺寸 */
    tableSize: String,
    /** 表头单元格类名自定义 */
    headerCellClass: [String, Function],
    /** 表头单元样式自定义 */
    headerCellStyle: [Object, Function],
    /** 表头单元格是否溢出省略 */
    headerEllipsis: Boolean,
    /** 表格行高 */
    rowHeight: Number
  },
  emits: {
    /** 多选框选中改变事件 */
    checkedChange: (_checked) => true,
    /** 列筛选改变事件 */
    filterChange: (_params) => true,
    /** 单元格点击事件 */
    cellClick: (_col, _e) => true,
    /** 单元格右键事件 */
    cellContextmenu: (_col, _e) => true,
    /** 单元格鼠标移入事件 */
    cellMouseenter: (_col, _e) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const getKey = (column, columnIndex) => {
      return `${props.headerIndex}-${String(column.key ?? columnIndex)}`;
    };
    const getFiltered = (column) => {
      return util.getColFiltered(column.originalCol, props.filtered);
    };
    const handleCellCheckedChange = (checked) => {
      emit("checkedChange", checked);
    };
    const handleCellFilterChange = (params) => {
      emit("filterChange", params);
    };
    const handleCellClick = (col, e) => {
      emit("cellClick", col, e);
    };
    const handleCellContextmenu = (col, e) => {
      emit("cellContextmenu", col, e);
    };
    const handleCellMouseenter = (col, e) => {
      emit("cellMouseenter", col, e);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.headerCols, (column, index) => {
        return vue.openBlock(), vue.createBlock(HeaderCell, {
          key: getKey(column, index),
          column,
          columnIndex: index,
          headerIndex: __props.headerIndex,
          colSize: __props.headerColSizes ? __props.headerColSizes[index] : void 0,
          sortBy: __props.sortBy,
          filterValue: getFiltered(column),
          isCheckAll: __props.isCheckAll,
          isIndeterminate: __props.isIndeterminate,
          disabledCheckbox: __props.disabledCheckbox,
          tableSize: __props.tableSize,
          headerCellClass: __props.headerCellClass,
          headerCellStyle: __props.headerCellStyle,
          headerEllipsis: __props.headerEllipsis,
          rowHeight: __props.rowHeight,
          onCheckedChange: handleCellCheckedChange,
          onFilterChange: handleCellFilterChange,
          onClick: handleCellClick,
          onContextmenu: handleCellContextmenu,
          onMouseenter: handleCellMouseenter
        }, vue.createSlots({ _: 2 }, [
          vue.renderList(Object.keys(_ctx.$slots), (name) => {
            return {
              name,
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, name, vue.mergeProps({ ref_for: true }, slotProps || {}))
              ])
            };
          })
        ]), 1032, ["column", "columnIndex", "headerIndex", "colSize", "sortBy", "filterValue", "isCheckAll", "isIndeterminate", "disabledCheckbox", "tableSize", "headerCellClass", "headerCellStyle", "headerEllipsis", "rowHeight"]);
      }), 128);
    };
  }
});
module.exports = _sfc_main;
