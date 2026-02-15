"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index$1 = require("../icons/index");
const common = require("../utils/common");
const util = require("./util");
const props = require("./props");
const ownSlots = ["default", "append", "empty"];
const index = /* @__PURE__ */ vue.defineComponent({
  name: "EleDataTable",
  props: props.dataTableProps,
  emits: props.dataTableEmits,
  setup(props$1, {
    emit,
    slots,
    expose
  }) {
    const events = util.useEmits(emit);
    const methods = util.useMethods(() => tableRef.value);
    const {
      isLayoutFixedHead,
      isLayoutMaximized
    } = util.useStickyHeader();
    const tableState = {
      sorter: props$1.defaultSort,
      key: null,
      checkedKeys: [],
      checked: [],
      reserveChecked: util.isReserveChecked(props$1.columns)
    };
    const tableRef = vue.ref(null);
    const tableCols = vue.ref(props$1.columns ?? []);
    const tableOverflowTooltip = vue.computed(() => {
      return util.getGlobalTooltipProps(props$1.showOverflowTooltip, props$1.tooltipEffect, props$1.tooltipOptions);
    });
    const childKey = vue.computed(() => {
      return props$1.treeProps?.children || "children";
    });
    const borderKey = vue.computed(() => {
      if (tableCols.value.some((col) => col.children?.length)) {
        return 1;
      }
      return props$1.border ? 1 : 0;
    });
    const tableProps = vue.computed(() => {
      const propKeys = props.tablePropKeys.filter((k) => !["currentRowKey", "showOverflowTooltip", "tooltipOptions", "tooltipEffect"].includes(k));
      return {
        ...common.pick(props$1, propKeys),
        ...common.omit(events, ["onUpdate:currentRowKey", "onUpdate:selectedRowKeys", "onRowClick", "onHeaderClick", "onSortChange", "onFilterChange", "onCurrentChange", "onSelect", "onSelectAll", "onSelectionChange"])
      };
    });
    const handleRowClick = (row, column, event) => {
      const disabled = util.isDisableRow(row, props$1.data.indexOf(row), props$1.columns);
      if (props$1.rowClickChecked && !disabled) {
        const selections = methods.getSelectionRows();
        if (props$1.rowClickChecked === "smart" && (!selections || !selections.length || selections.length === 1)) {
          const key = common.getValue(row, props$1.rowKey);
          updateCheckedState(key == null ? [] : [key]);
        } else {
          toggleRowSelection(row);
        }
      }
      events.onRowClick(row, column, event, disabled, methods.getSelectionRows());
    };
    const handleHeaderClick = (column, e) => {
      if (column.sortable && column.filters) {
        const el = e.currentTarget;
        if (el) {
          const caretEl = el.querySelector(".caret-wrapper");
          caretEl && caretEl.dispatchEvent(new MouseEvent("click"));
        }
      }
      events.onHeaderClick(column, e);
    };
    const handleSortChange = (sorter) => {
      const currentSorter = tableState.sorter;
      if (currentSorter && sorter.prop === currentSorter.prop && sorter.order === currentSorter.order) {
        return;
      }
      tableState.sorter = sorter;
      events.onSortChange(sorter);
    };
    const handleFilterChange = (filter) => {
      tableState.filter = util.getTableFilter(tableRef.value) ?? filter;
      events.onFilterChange(tableState.filter);
    };
    const handleCurrentChange = (row, old) => {
      if (row != null && row !== old) {
        updateSelectedState(common.getValue(row, props$1.rowKey), row);
      }
    };
    const handleSelect = (selection, row) => {
      events.onSelect(selection, row);
      updateCheckedState(util.getRowKeys(selection, props$1.rowKey), selection);
    };
    const handleSelectAll = (selection) => {
      updateCheckedState(util.getRowKeys(selection, props$1.rowKey), selection);
      events.onSelectAll(selection);
    };
    const updateScrollBar = () => {
      const scrollBarRef = tableRef.value?.scrollBarRef;
      if (scrollBarRef && typeof scrollBarRef.update === "function") {
        scrollBarRef.update();
      }
    };
    const clearSort = () => {
      methods.clearSort();
      tableState.sorter = {};
    };
    const clearSelection = () => {
      updateCheckedState([]);
    };
    const toggleRowSelection = (row, selected, ignoreSelectable) => {
      methods.toggleRowSelection(row, selected, ignoreSelectable);
      const selection = methods.getSelectionRows() || [];
      updateCheckedState(util.getRowKeys(selection, props$1.rowKey), selection);
    };
    const setCurrentRow = (row) => {
      updateSelectedState(common.getValue(row, props$1.rowKey), row);
    };
    const setCurrentRowKey = (key) => {
      updateSelectedState(key);
    };
    const getCurrentRow = () => {
      return tableState.row;
    };
    const setSelectedRows = (rows) => {
      if (rows) {
        updateCheckedState(util.getRowKeys(rows, props$1.rowKey), rows, !!rows.length);
      }
    };
    const setSelectedRowKeys = (keys) => {
      if (keys) {
        updateCheckedState(keys);
      }
    };
    const toggleRowExpansionAll = (expanded) => {
      common.eachTree(props$1.data, (row) => {
        if (row[childKey.value]?.length) {
          methods.toggleRowExpansion(row, expanded);
        }
      }, childKey.value);
    };
    const updateSelectedState = (key, item) => {
      if (!util.valueIsChanged(tableState.key, key)) {
        if (key != null && item != null) {
          if (tableState.row !== item) {
            tableState.row = item;
            events.onCurrentChange(item, tableState.oldRow);
          }
          methods.setCurrentRow(item);
        }
        return;
      }
      if (key != null) {
        const row = util.getRowByKey(key, props$1.data, props$1.rowKey, childKey.value);
        if (row != null || props$1.reserveCurrent) {
          tableState.oldRow = tableState.row;
          tableState.row = row || item || void 0;
          if (tableState.row == null && props$1.cacheData != null) {
            tableState.row = util.getRowByKey(key, props$1.cacheData, props$1.rowKey, childKey.value);
          }
          tableState.key = key;
          methods.setCurrentRow(row);
          updateCurrentRowKey(key);
          events.onCurrentChange(tableState.row, tableState.oldRow);
          return;
        }
      }
      if (tableState.key != null) {
        tableState.oldRow = tableState.row;
        tableState.row = void 0;
        tableState.key = null;
        methods.setCurrentRow(null);
        updateCurrentRowKey();
        events.onCurrentChange(void 0, tableState.oldRow);
      }
    };
    const updateCheckedState = (keys, items, force) => {
      if (!force && !util.arrayIsChanged(tableState.checkedKeys, keys)) {
        return;
      }
      const [dataKeys, list] = util.getKeysAndList(props$1.data, props$1.rowKey, childKey.value);
      const [cacheKeys, cacheList] = util.getKeysAndList(props$1.cacheData, props$1.rowKey, childKey.value);
      const itemKeys = items ? items.map((d) => common.getValue(d, props$1.rowKey)) : [];
      const oldKeys = tableState.checked.map((d) => common.getValue(d, props$1.rowKey));
      const checkedKeys = [];
      const checked = [];
      keys.forEach((key) => {
        const index2 = dataKeys.indexOf(key);
        if (index2 !== -1) {
          checkedKeys.push(key);
          checked.push(list[index2]);
        } else if (tableState.reserveChecked) {
          checkedKeys.push(key);
          if (items != null) {
            const tIndex = itemKeys.indexOf(key);
            if (tIndex !== -1 && !items[tIndex]._isMock) {
              checked.push(items[tIndex]);
              return;
            }
          }
          if (props$1.cacheData != null) {
            const i = cacheKeys.indexOf(key);
            if (i !== -1) {
              checked.push(cacheList[i]);
              return;
            }
          }
          const oIndex = oldKeys.indexOf(key);
          if (oIndex !== -1) {
            checked.push(tableState.checked[oIndex]);
            return;
          }
          if (typeof props$1.rowKey === "string") {
            checked.push({
              [props$1.rowKey]: key,
              _isMock: true
            });
          }
        }
      });
      const isChanged = util.arrayIsChanged(tableState.checked, checked);
      tableState.checked = checked;
      tableState.checkedKeys = checkedKeys;
      if (isChanged || force && util.arrayIsChanged(methods.getSelectionRows(), checked)) {
        methods.clearSelection();
        checked.forEach((row) => {
          util.toggleRowSelectionPro(tableRef.value, row, true);
        });
      }
      updateSelectedRowKeys(checkedKeys);
      if (isChanged) {
        events.onSelectionChange(checked);
      }
    };
    const updateSelectedAndChecked = () => {
      const key = tableState.key;
      if (key != null) {
        const row = util.getRowByKey(key, props$1.data, props$1.rowKey, childKey.value);
        if (row != null) {
          updateSelectedState(key, row);
        } else if (!props$1.reserveCurrent) {
          updateSelectedState(null);
        } else if (props$1.cacheData != null) {
          const temp = util.getRowByKey(key, props$1.cacheData, props$1.rowKey, childKey.value);
          if (temp != null) {
            updateSelectedState(key, temp);
          }
        }
      }
      if (tableState.checkedKeys.length) {
        updateCheckedState(tableState.checkedKeys, void 0, true);
      }
    };
    const updateCurrentRowKey = (key) => {
      if (util.valueIsChanged(props$1.currentRowKey, key)) {
        events["onUpdate:currentRowKey"](key);
      }
    };
    const updateSelectedRowKeys = (keys) => {
      const selected = props$1.selectedRowKeys || [];
      if (util.arrayIsChanged(selected, keys)) {
        events["onUpdate:selectedRowKeys"](keys);
      }
    };
    vue.watch(() => props$1.columns, (columns) => {
      tableState.reserveChecked = util.isReserveChecked(columns);
      if (!columns) {
        tableCols.value = [];
      } else {
        const {
          cols,
          sorter
        } = util.getStateCols(columns, tableState.sorter, tableState.filter);
        tableCols.value = cols;
        vue.nextTick(() => {
          methods.doLayout();
          updateScrollBar();
          if (sorter) {
            methods.sort(sorter.prop, sorter.order || "ascending");
          }
        });
      }
    }, {
      deep: true
    });
    vue.watch([() => props$1.data, () => props$1.cacheData], () => {
      vue.nextTick(() => {
        updateSelectedAndChecked();
        if (props$1.defaultExpandAll) {
          toggleRowExpansionAll(true);
        }
      });
    });
    vue.watch(() => props$1.currentRowKey, (key) => {
      updateSelectedState(key);
    });
    vue.watch(() => props$1.selectedRowKeys, (selectedRowKeys) => {
      updateCheckedState(selectedRowKeys || []);
    }, {
      deep: true
    });
    vue.onMounted(() => {
      if (props$1.currentRowKey != null) {
        updateSelectedState(props$1.currentRowKey);
      }
      if (props$1.selectedRowKeys != null && props$1.selectedRowKeys.length) {
        updateCheckedState(props$1.selectedRowKeys);
      }
    });
    const exposeValue = {
      ...methods,
      clearSort,
      clearSelection,
      toggleRowSelection,
      setCurrentRow,
      setCurrentRowKey,
      getCurrentRow,
      setSelectedRows,
      setSelectedRowKeys,
      toggleRowExpansionAll,
      updateSelectedAndChecked,
      tableRef
    };
    expose(exposeValue);
    const renderTableColumn = (col) => {
      return vue.createVNode(elementPlus.ElTableColumn, vue.mergeProps(common.omit(col, ["showOverflowTooltip", "filterClassName", "columnKey", "className", "uid", "slot", "headerSlot", "hideInTable", "hideInSetting", "hideInExport", "hideInPrint", "printSlot", "children"]), {
        "key": col.uid ?? col.columnKey ?? col.prop,
        "index": col.index ?? props$1.pageIndex,
        "className": util.getCellClass(col),
        "columnKey": col.columnKey ?? col.prop,
        "filterClassName": util.getFilterPopperClass(col.filterClassName),
        "showOverflowTooltip": util.getTooltipProps(col.showOverflowTooltip, tableOverflowTooltip.value)
      }), {
        header: (slotProps) => vue.createVNode("div", {
          "class": "ele-cell-title",
          "title": slotProps?.column?.label
        }, [col.headerSlot && !ownSlots.includes(col.headerSlot) && slots[col.headerSlot] ? slots[col.headerSlot]?.(slotProps) : slotProps?.column?.label]),
        ["filter-icon"]: (slotProps) => !col.filterIcon ? vue.createVNode(index$1.FilterFilled, null, null) : typeof col.filterIcon === "string" && !ownSlots.includes(col.filterIcon) && slots[col.filterIcon] ? slots[col.filterIcon]?.(slotProps) : vue.h(col.filterIcon),
        default: col.children && col.children.length ? () => col?.children?.map?.(renderTableColumn) : col.slot && !ownSlots.includes(col.slot) && slots[col.slot] ? (slotProps) => (!props$1.slotNormalize || slotProps?.$index != -1) && col.slot ? slots[col.slot]?.(slotProps) : void 0 : void 0
      });
    };
    return () => vue.createVNode(elementPlus.ElTable, vue.mergeProps({
      "key": borderKey.value
    }, tableProps.value, {
      "ref": tableRef,
      "emptyText": props$1.errorText || props$1.emptyText,
      "rowClassName": (param) => util.getBodyRowClass(props$1.rowClassName, param),
      "headerRowClassName": (param) => util.getHeadRowClass(props$1.headerRowClassName, param, props$1.headerEllipsis),
      "class": ["ele-data-table", {
        "is-sticky": props$1.sticky
      }, {
        "is-layout-fixed-head": props$1.sticky && isLayoutFixedHead.value
      }, {
        "is-layout-maximized": props$1.sticky && isLayoutMaximized.value
      }, {
        "is-sticky": props$1.sticky
      }, {
        "hide-header": !props$1.showHeader
      }, {
        "hide-bottom-line": !props$1.bottomLine
      }],
      "onRowClick": handleRowClick,
      "onHeaderClick": handleHeaderClick,
      "onSortChange": handleSortChange,
      "onFilterChange": handleFilterChange,
      "onCurrentChange": handleCurrentChange,
      "onSelect": handleSelect,
      "onSelectAll": handleSelectAll
    }), {
      append: slots.append ? (slotProps) => slots.append?.(slotProps) : void 0,
      empty: slots.empty ? () => slots.empty?.({
        text: props$1.emptyText,
        error: props$1.errorText
      }) : props$1.emptyProps ? () => vue.createVNode(elementPlus.ElEmpty, vue.mergeProps({
        "imageSize": 68
      }, !props$1.emptyProps || props$1.emptyProps === true ? {} : props$1.emptyProps, {
        "description": props$1.errorText || props$1.emptyText,
        "class": "ele-table-empty"
      }), null) : void 0,
      default: () => tableCols.value.map(renderTableColumn)
    });
  }
});
module.exports = index;
