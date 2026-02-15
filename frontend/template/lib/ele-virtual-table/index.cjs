"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const EleTooltip = require("../ele-tooltip/index");
const util = require("../ele-data-table/util");
const util$1 = require("./util");
const HeaderRow = require("./components/header-row");
const BodyRow = require("./components/body-row");
const ExpandRow = require("./components/expand-row");
const FooterRow = require("./components/footer-row");
const props = require("./props");
const _hoisted_1 = {
  key: 0,
  class: "ele-table-empty-text"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleVirtualTable" },
  __name: "index",
  props: props.virtualTableProps,
  emits: props.virtualTableEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const ownSlots = ["default", "empty", "append"];
    const props2 = __props;
    const emit = __emit;
    const { t } = elementPlus.useLocale();
    const events = util.useEmits(emit);
    const [wrapWidth, wrapHeight, updateWrapSize] = hook.useResizeObserver({
      getEl: () => rootRef.value
    });
    const { isLayoutFixedHead, isLayoutMaximized } = util.useStickyHeader();
    const tableState = {
      checked: /* @__PURE__ */ new Map(),
      reserveChecked: false,
      scrollTop: 0,
      sorter: util$1.getDefaultSorter(props2.defaultSort, props2.columns)
    };
    const rootRef = vue.ref(null);
    const tableRef = vue.ref(null);
    const tableKey = vue.ref(0);
    const headerRows = vue.ref([]);
    const bodyCols = vue.ref([]);
    const headerRowSizes = vue.ref([]);
    const bodyColSizes = vue.ref([]);
    const colsSumWidth = vue.ref(0);
    const tableWidth = vue.ref(0);
    const tableHeight = vue.ref(0);
    const tableData = vue.ref([]);
    const tableCurrentData = vue.ref([]);
    const tableColumns = vue.ref([]);
    const tableScrollLeft = vue.ref(0);
    const selectedRowKey = vue.ref(props2.currentRowKey ?? null);
    const checkedRowKeys = vue.ref(
      new Set(props2.selectedRowKeys || [])
    );
    const isCheckAll = vue.ref(false);
    const expandedRowKeys = vue.ref([]);
    const sortBy = vue.ref(
      util$1.getDefaultSort(props2.defaultSort)
    );
    const filtered = vue.reactive(util$1.getDefaultFiltered(props2.columns));
    const tableTooltipProps = vue.reactive({
      placement: "top",
      trigger: "click",
      offset: 0,
      hideAfter: 0,
      content: "",
      virtualRef: void 0,
      virtualTriggering: true,
      disabled: true,
      visible: false,
      teleported: false,
      transition: "ele-transition-none"
    });
    const treeTableProps = vue.computed(() => {
      return util$1.getTreeProps(props2.treeProps);
    });
    const treeChildrenName = vue.computed(() => {
      return treeTableProps.value.childrenName;
    });
    const treeHasChildrenName = vue.computed(() => {
      return treeTableProps.value.hasChildrenName;
    });
    const isTreeData = vue.computed(() => {
      return tableData.value.some(
        (d) => d.children?.length || props2.lazy && d.hasChildren
      );
    });
    const tableExpandCol = vue.computed(() => {
      return bodyCols.value.find((d) => {
        return !!(d && d.originalCol && d.originalCol.type === "expand");
      });
    });
    const hasExpandCol = vue.computed(() => {
      return !!tableExpandCol.value;
    });
    const tableExpandColumnKey = vue.computed(() => {
      if (tableExpandCol.value) {
        return tableExpandCol.value.key;
      }
      if (!isTreeData.value) {
        return;
      }
      const treeCol = bodyCols.value.find((d) => {
        if (!d || !d.key || !d.originalCol) {
          return false;
        }
        const colType = d.originalCol.type;
        return !colType || !["selection", "index"].includes(colType);
      });
      return treeCol ? treeCol.key : void 0;
    });
    const tableRowHeight = vue.computed(() => {
      return util$1.getRowHeight(props2.size, props2.rowHeight);
    });
    const autoRowHeight = vue.computed(() => {
      return util$1.isAutoRowHeight(
        hasExpandCol.value,
        bodyCols.value,
        props2.showOverflowTooltip
      );
    });
    const headerNums = vue.computed(() => {
      return props2.showHeader ? headerRows.value.length : 0;
    });
    const hasFooter = vue.computed(() => {
      return !!(props2.showSummary && tableCurrentData.value.length);
    });
    const tableProps = vue.computed(() => {
      const rowHeight = tableRowHeight.value;
      const headerHeight = new Array(headerNums.value).fill(rowHeight);
      const opt = {
        cache: 2,
        estimatedRowHeight: autoRowHeight.value ? rowHeight : void 0,
        headerClass: ((params) => {
          const rowClass = props2.headerRowClassName;
          const classes = ["ele-table-head-tr"];
          if (typeof rowClass === "function") {
            const custom = rowClass({ rowIndex: params.headerIndex });
            if (custom) {
              classes.push(custom);
            }
          } else if (typeof rowClass === "string" && rowClass) {
            classes.push(rowClass);
          }
          return classes.join(" ");
        }),
        headerProps: (params) => {
          const opt2 = { rowIndex: params.headerIndex };
          const style = props2.headerRowStyle;
          return { style: typeof style === "function" ? style(opt2) : style };
        },
        //headerCellProps: void 0,
        headerHeight: headerNums.value ? headerHeight : 0,
        footerHeight: hasFooter.value ? rowHeight : void 0,
        rowClass: ((params) => {
          const classes = ["ele-table-tr"];
          const row = params.rowData;
          const rowIndex = row.rowIndex;
          if (row && row.isExpandRow === true) {
            classes.push("is-expand-row");
          } else if (row) {
            if (props2.stripe && (rowIndex + 1) % 2 === 0) {
              classes.push("is-even");
            }
            if (props2.highlightCurrentRow && selectedRowKey.value != null && selectedRowKey.value === row.rowId) {
              classes.push("is-current");
            }
            const rowClass = props2.rowClassName;
            if (typeof rowClass === "function") {
              const custom = rowClass({ row: row.rowData, rowIndex });
              if (custom) {
                classes.push(custom);
              }
            } else if (typeof rowClass === "string" && rowClass) {
              classes.push(rowClass);
            }
          }
          return classes.join(" ");
        }),
        rowKey: "rowId",
        rowProps: (params) => {
          const row = params.rowData;
          const opt2 = { row: row.rowData, rowIndex: row.rowIndex };
          const style = props2.rowStyle;
          return { style: typeof style === "function" ? style(opt2) : style };
        },
        rowHeight: autoRowHeight.value ? void 0 : rowHeight,
        //cellProps: void 0,
        columns: tableColumns.value,
        data: tableCurrentData.value,
        //dataGetter: void 0,
        //fixedData: void 0,
        expandColumnKey: tableExpandColumnKey.value,
        expandedRowKeys: expandedRowKeys.value,
        defaultExpandedRowKeys: expandedRowKeys.value,
        //class: void 0,
        fixed: true,
        width: tableWidth.value,
        height: tableHeight.value,
        //maxHeight: void 0,
        hScrollbarSize: 0,
        vScrollbarSize: 0,
        scrollbarAlwaysOn: props2.scrollbarAlwaysOn,
        sortBy: sortBy.value
        //sortState: void 0
      };
      return opt;
    });
    const isIndeterminate = vue.computed(() => {
      return !!(checkedRowKeys.value.size && !isCheckAll.value);
    });
    const isPingLeft = vue.computed(() => {
      return tableScrollLeft.value > 1;
    });
    const isPingRight = vue.computed(() => {
      const scrollWidth = colsSumWidth.value - tableWidth.value - 1;
      return scrollWidth > 1 && tableScrollLeft.value < scrollWidth;
    });
    const tableSumText = vue.computed(() => {
      return props2.sumText ?? t("el.table.sumText");
    });
    const tableEmptyText = vue.computed(() => {
      return props2.errorText || props2.emptyText || t("el.table.emptyText");
    });
    const hideTooltip = () => {
      tableTooltipProps.visible = false;
      tableTooltipProps.disabled = true;
    };
    const triggerTooltip = (cell, col) => {
      const cellText = cell.innerText;
      const tooltip = util.mergeTooltipProps(
        col ? col.showOverflowTooltip : void 0,
        util.getGlobalTooltipProps(
          props2.showOverflowTooltip,
          props2.tooltipEffect,
          props2.tooltipOptions
        )
      );
      if (cellText && !!tooltip && util$1.cellIsOverflow(cell)) {
        tableTooltipProps.content = cellText;
        const excludes = [
          "virtualRef",
          "virtualTriggering",
          "disabled",
          "visible",
          "teleported"
        ];
        Object.keys(tooltip).forEach((key) => {
          const value = tooltip[key];
          if (!excludes.includes(key) && tableTooltipProps[key] !== value) {
            tableTooltipProps[key] = value;
          }
        });
        tableTooltipProps.virtualRef = cell;
        tableTooltipProps.disabled = false;
        tableTooltipProps.visible = true;
      } else {
        hideTooltip();
      }
    };
    const sortAndFilterTableData = (sorter) => {
      if (sorter && tableState.sorter !== sorter) {
        tableState.sorter = sorter;
      }
      let data = [...tableData.value];
      if (tableState.sorter) {
        const { prop, order, column: col } = tableState.sorter;
        if (col?.sortable === true) {
          const reverse = order === "descending" ? -1 : 1;
          data.sort((a, b) => {
            if (!order) {
              return a.rowIndex - b.rowIndex;
            }
            const v = util$1.getSortCompareValue(col.sortMethod, a, b, prop);
            return v * reverse;
          });
        }
      }
      Object.keys(filtered).forEach((key) => {
        const col = util$1.getColumnByKey(props2.columns, key);
        const filterMethod = col?.filterMethod;
        const values = filtered[key];
        if (!values?.length || !filterMethod) {
          return;
        }
        data = data.filter((d) => {
          const row = d.rowData;
          return values.some((value) => filterMethod(value, row, col));
        });
      });
      tableCurrentData.value = data;
    };
    const handleTableFilterChange = (params) => {
      const key = util$1.getColKey(params.column);
      if (key) {
        filtered[key] = params.value;
        sortAndFilterTableData();
        events.onFilterChange(filtered);
      }
    };
    const handleCellCheckedChange = (row, checked) => {
      toggleSelected(row.rowData, row.rowId, checked);
      const selection = getSelectionRows();
      events.onSelect(selection, row.rowData);
      events.onSelectionChange(selection);
    };
    const handleCellExpandChange = (row, expanded, children) => {
      if (expanded && children != null) {
        const childs = util$1.transformTableData(
          children,
          hasExpandCol.value,
          treeChildrenName.value,
          treeHasChildrenName.value,
          props2.rowKey,
          util$1.getSelectableFunction(bodyCols.value)
        );
        let index = -1;
        common.eachTree(tableData.value, (d) => {
          index++;
          if (d.rowId === row.rowId) {
            d.children = childs;
            if (!childs.length) {
              d.hasChildren = false;
            }
          }
          d.rowIndex = index;
        });
        if (!childs.length) {
          return;
        }
      }
      toggleRowExpansion(row, expanded);
    };
    const handleCellClick = (row, col, e) => {
      const cell = e.currentTarget;
      const rowData = row.rowData;
      const rowDataKey = row.rowId;
      events.onCellClick(rowData, col, cell, e);
      if (props2.highlightCurrentRow) {
        setCurrentRow(rowData);
      }
      if (props2.rowClickChecked && !row.isDisabled) {
        if (props2.rowClickChecked === "smart" && (!checkedRowKeys.value.size || checkedRowKeys.value.size === 1)) {
          if (rowDataKey != null && !checkedRowKeys.value.has(rowDataKey)) {
            checkedRowKeys.value = /* @__PURE__ */ new Set([rowDataKey]);
            tableState.checked.clear();
            tableState.checked.set(rowDataKey, rowData);
            updateIsCheckAll();
            updateSelectedRowKeys([rowDataKey]);
            events.onSelectionChange([rowData]);
          }
        } else {
          toggleSelected(rowData, rowDataKey);
          events.onSelectionChange(getSelectionRows());
        }
      }
      events.onRowClick(rowData, col, e, row.isDisabled, getSelectionRows());
    };
    const handleCellDblclick = (row, col, e) => {
      const cell = e.currentTarget;
      events.onCellDblclick(row.rowData, col, cell, e);
      events.onRowDblclick(row.rowData, col, e);
    };
    const handleCellContextmenu = (row, col, e) => {
      const cell = e.currentTarget;
      events.onCellContextmenu(row.rowData, col, cell, e);
      events.onRowContextmenu(row.rowData, col, e);
    };
    const handleCellMouseenter = (row, col, e) => {
      const cell = e.currentTarget;
      triggerTooltip(cell, col);
      events.onCellMouseEnter(row.rowData, col, cell, e);
    };
    const handleCellMouseleave = (row, col, e) => {
      const cell = e.currentTarget;
      events.onCellMouseLeave(row.rowData, col, cell, e);
    };
    const handleHeaderCellClick = (col, e) => {
      if (col && (col.sortable === true || col.sortable === "custom")) {
        sortBy.value = util$1.getSortBy(sortBy.value, col);
        const prop = col.property || col.prop;
        const order = util$1.getOrderValue(
          sortBy.value ? sortBy.value.order : void 0
        );
        const sorter = { prop, order, column: col };
        sortAndFilterTableData(sorter);
        events.onSortChange(sorter);
      }
      events.onHeaderClick(col, e);
    };
    const handleHeaderCellContextmenu = (col, e) => {
      events.onHeaderContextmenu(col, e);
    };
    const handleHeaderCellMouseenter = () => {
      hideTooltip();
    };
    const handleFooterCellMouseenter = (e) => {
      triggerTooltip(e.currentTarget, { showOverflowTooltip: true });
    };
    const handleExpandCellMouseenter = () => {
      hideTooltip();
    };
    const handleTableMouseleave = () => {
      hideTooltip();
    };
    const handleTableScroll = (option) => {
      tableState.scrollTop = option.scrollTop;
      const scrollLeft = option.scrollLeft;
      if (tableScrollLeft.value !== scrollLeft) {
        tableScrollLeft.value = scrollLeft;
      }
      if (hasFooter.value && tableRef.value && tableRef.value.$el) {
        const el = common.queryChild(tableRef.value.$el, "el-table-v2__footer");
        if (el && el.scrollLeft != scrollLeft) {
          el.scrollLeft = scrollLeft;
        }
      }
      emit("scroll", option);
    };
    const handleEndEeached = (params) => {
      emit("endEeached", params);
    };
    const handleRowsRendered = (params) => {
      emit("rowsRendered", params);
    };
    const updateTableData = () => {
      tableData.value = util$1.transformTableData(
        props2.data,
        hasExpandCol.value,
        treeChildrenName.value,
        treeHasChildrenName.value,
        props2.rowKey,
        util$1.getSelectableFunction(bodyCols.value)
      );
      sortAndFilterTableData();
      if (props2.defaultExpandAll) {
        toggleRowExpansionAll(true);
      } else if (props2.expandRowKeys && props2.expandRowKeys.length) {
        expandedRowKeys.value = [...props2.expandRowKeys];
      } else {
        toggleRowExpansionAll(false);
      }
    };
    const updateSelectedState = (key, item) => {
      if (!util.valueIsChanged(selectedRowKey.value, key)) {
        if (key != null && item != null && tableState.row !== item) {
          tableState.row = item;
          events.onCurrentChange(item, tableState.oldRow);
        }
        return;
      }
      if (key != null) {
        const row = util$1.getRowByKey(key, tableData.value);
        if (row != null || props2.reserveCurrent) {
          tableState.oldRow = tableState.row;
          tableState.row = row?.rowData || item || void 0;
          if (tableState.row == null && props2.cacheData != null) {
            tableState.row = util$1.getRowByKey(
              key,
              props2.cacheData,
              props2.rowKey,
              treeChildrenName.value
            );
          }
          selectedRowKey.value = key;
          updateCurrentRowKey(key);
          events.onCurrentChange(tableState.row, tableState.oldRow);
          return;
        }
      }
      if (selectedRowKey.value != null) {
        tableState.oldRow = tableState.row;
        tableState.row = void 0;
        selectedRowKey.value = null;
        updateCurrentRowKey();
        events.onCurrentChange(void 0, tableState.oldRow);
      }
    };
    const updateSelectedAndChecked = () => {
      const key = selectedRowKey.value;
      if (key != null) {
        const row = util$1.getRowByKey(key, tableData.value);
        if (row != null) {
          updateSelectedState(key, row.rowData);
        } else if (!props2.reserveCurrent) {
          updateSelectedState(null);
        } else if (props2.cacheData != null) {
          const temp = util$1.getRowByKey(
            key,
            props2.cacheData,
            props2.rowKey,
            treeChildrenName.value
          );
          if (temp != null) {
            updateSelectedState(key, temp);
          }
        }
      }
      if (checkedRowKeys.value.size) {
        const oldSelection = getSelectionRows();
        const deletedKeys = [];
        const [dataKeys, list] = util$1.getKeysAndList(tableData.value);
        const [cacheKeys, cacheList] = util$1.getKeysAndList(
          props2.cacheData,
          props2.rowKey,
          treeChildrenName.value
        );
        checkedRowKeys.value.forEach((key2) => {
          const index = dataKeys.indexOf(key2);
          if (index !== -1) {
            const row = list[index].rowData;
            if (tableState.checked.get(key2) !== row) {
              tableState.checked.set(key2, row);
            }
          } else if (!tableState.reserveChecked) {
            deletedKeys.push(key2);
          } else if (props2.cacheData != null) {
            const i = cacheKeys.indexOf(key2);
            const temp = i !== -1 ? cacheList[i] : void 0;
            if (i !== -1 && tableState.checked.get(key2) !== temp) {
              tableState.checked.set(key2, temp);
            }
          }
        });
        deletedKeys.forEach((key2) => {
          checkedRowKeys.value.delete(key2);
          tableState.checked.delete(key2);
        });
        updateIsCheckAll();
        if (deletedKeys.length) {
          updateSelectedRowKeys(Array.from(checkedRowKeys.value));
        }
        const selection = getSelectionRows();
        if (util.arrayIsChanged(oldSelection, selection)) {
          events.onSelectionChange(selection);
        }
      }
    };
    const updateIsCheckAll = () => {
      if (!tableData.value.length || !checkedRowKeys.value.size) {
        isCheckAll.value = false;
        return;
      }
      const unchecked = common.findTree(
        tableData.value,
        (d) => !d.isExpandRow && !d.isDisabled && d.rowId != null && !checkedRowKeys.value.has(d.rowId)
      );
      isCheckAll.value = unchecked == null;
    };
    const toggleSelected = (row, rowDataKey, selected) => {
      const isChecked = checkedRowKeys.value.has(rowDataKey);
      const checked = selected == null ? !isChecked : selected;
      if (checked === isChecked) {
        return;
      }
      if (checked) {
        checkedRowKeys.value.add(rowDataKey);
        tableState.checked.set(rowDataKey, row);
      } else {
        checkedRowKeys.value.delete(rowDataKey);
        tableState.checked.delete(rowDataKey);
      }
      updateIsCheckAll();
      updateSelectedRowKeys(Array.from(checkedRowKeys.value));
    };
    const setSelectedRows = (rows) => {
      if (!rows || !util.arrayIsChanged(getSelectionRows(), rows)) {
        return;
      }
      if (tableState.reserveChecked) {
        const oldSelection = getSelectionRows();
        checkedRowKeys.value.clear();
        tableState.checked.clear();
        rows.forEach((r) => {
          const k = common.getValue(r, props2.rowKey);
          if (k != null) {
            checkedRowKeys.value.add(k);
            tableState.checked.set(k, r);
          }
        });
        updateIsCheckAll();
        updateSelectedRowKeys(Array.from(checkedRowKeys.value));
        const selection = getSelectionRows();
        if (util.arrayIsChanged(oldSelection, selection)) {
          events.onSelectionChange(selection);
        }
        return;
      }
      setSelectedRowKeys(util.getRowKeys(rows, props2.rowKey));
    };
    const setSelectedRowKeys = (keys) => {
      if (!keys || !util.arrayIsChanged(Array.from(checkedRowKeys.value), keys)) {
        return;
      }
      const oldSelection = getSelectionRows();
      if (tableState.reserveChecked) {
        const [dataKeys, list] = util$1.getKeysAndList(tableData.value);
        const [cacheKeys, cacheList] = util$1.getKeysAndList(
          props2.cacheData,
          props2.rowKey,
          treeChildrenName.value
        );
        checkedRowKeys.value = new Set(keys);
        tableState.checked.clear();
        keys.forEach((key) => {
          const index = dataKeys.indexOf(key);
          if (index !== -1) {
            tableState.checked.set(key, list[index].rowData);
          } else if (props2.cacheData != null) {
            const i = cacheKeys.indexOf(key);
            if (i !== -1) {
              tableState.checked.set(key, cacheList[i]);
            }
          }
        });
      } else {
        checkedRowKeys.value.clear();
        tableState.checked.clear();
        if (keys.length) {
          common.eachTree(tableData.value, (d) => {
            if (!d.isExpandRow && d.rowId != null && keys.includes(d.rowId)) {
              checkedRowKeys.value.add(d.rowId);
              tableState.checked.set(d.rowId, d.rowData);
            }
          });
        }
      }
      updateIsCheckAll();
      updateSelectedRowKeys(Array.from(checkedRowKeys.value));
      const selection = getSelectionRows();
      if (util.arrayIsChanged(oldSelection, selection)) {
        events.onSelectionChange(selection);
      }
    };
    const toggleRowExpansionAll = (expanded) => {
      if (!expanded) {
        if (expandedRowKeys.value.length) {
          expandedRowKeys.value = [];
          events.onExpandChange(void 0, []);
        }
        return;
      }
      const keys = [];
      const rows = [];
      common.eachTree(tableData.value, (row) => {
        if (row.children && row.children.length && row.rowId != null) {
          keys.push(row.rowId);
          rows.push(row.rowData);
        }
      });
      expandedRowKeys.value = keys;
      events.onExpandChange(void 0, rows);
    };
    const clearSelection = () => {
      if (checkedRowKeys.value.size) {
        const isChanged = !!tableState.checked.size;
        checkedRowKeys.value.clear();
        tableState.checked.clear();
        isCheckAll.value = false;
        updateSelectedRowKeys([]);
        if (isChanged) {
          events.onSelectionChange([]);
        }
      }
    };
    const getSelectionRows = () => {
      return Array.from(tableState.checked.values());
    };
    const toggleRowSelection = (row, selected) => {
      const key = common.getValue(row, props2.rowKey);
      if (key == null || !tableState.reserveChecked && !util$1.getRowByKey(key, tableData.value)) {
        return;
      }
      const oldSelection = getSelectionRows();
      toggleSelected(row, key, selected);
      const selection = getSelectionRows();
      if (util.arrayIsChanged(oldSelection, selection)) {
        events.onSelectionChange(selection);
      }
    };
    const toggleAllSelection = () => {
      if (!tableData.value.length) {
        return;
      }
      if (isCheckAll.value || isIndeterminate.value && !props2.selectOnIndeterminate) {
        if (checkedRowKeys.value.size) {
          if (tableState.reserveChecked) {
            common.eachTree(tableData.value, (d) => {
              if (!d.isExpandRow && d.rowId != null) {
                checkedRowKeys.value.delete(d.rowId);
                tableState.checked.delete(d.rowId);
              }
            });
            isCheckAll.value = false;
            updateSelectedRowKeys(Array.from(checkedRowKeys.value));
            const selection2 = getSelectionRows();
            events.onSelectionChange(selection2);
            events.onSelectAll(selection2);
          } else {
            clearSelection();
            events.onSelectAll([]);
          }
        }
        return;
      }
      common.eachTree(tableData.value, (d) => {
        if (!d.isExpandRow && !d.isDisabled && d.rowId != null) {
          checkedRowKeys.value.add(d.rowId);
          tableState.checked.set(d.rowId, d.rowData);
        }
      });
      isCheckAll.value = true;
      updateSelectedRowKeys(Array.from(checkedRowKeys.value));
      const selection = getSelectionRows();
      events.onSelectionChange(selection);
      events.onSelectAll(selection);
    };
    const toggleRowExpansion = (row, expanded) => {
      const dataKey = row.rowId;
      const isSpread = expandedRowKeys.value.includes(dataKey);
      const spread = expanded == null ? !isSpread : expanded;
      if (spread === isSpread) {
        return;
      }
      if (spread) {
        expandedRowKeys.value.push(dataKey);
      } else {
        const index = expandedRowKeys.value.findIndex((t2) => t2 === dataKey);
        expandedRowKeys.value.splice(index, 1);
      }
      events.onExpandChange(row.rowData, spread);
    };
    const setCurrentRow = (row) => {
      updateSelectedState(common.getValue(row, props2.rowKey), row);
    };
    const setCurrentRowKey = (key) => {
      updateSelectedState(key);
    };
    const getCurrentRow = () => {
      return tableState.row;
    };
    const clearSort = () => {
      if (sortBy.value != null) {
        sortBy.value = void 0;
        tableState.sorter = void 0;
        sortAndFilterTableData();
      }
    };
    const clearFilter = (columnKeys) => {
      const keys = columnKeys == null ? Object.keys(filtered) : columnKeys;
      keys.forEach((key) => {
        const v = filtered[key];
        if (v == null || v.length) {
          filtered[key] = [];
        }
      });
      sortAndFilterTableData();
    };
    const doLayout = (force) => {
      const { width, sumWidth, rowSizes, colSizes } = util$1.computeColSizes(
        bodyCols.value,
        headerRows.value,
        wrapWidth.value
      );
      if (!width) {
        return;
      }
      const isUpdate = colsSumWidth.value && colsSumWidth.value !== sumWidth;
      const isSizesChanged = util$1.colSizesIsChanged(bodyColSizes.value, colSizes);
      tableWidth.value = width;
      colsSumWidth.value = sumWidth;
      headerRowSizes.value = rowSizes;
      if (force || isSizesChanged) {
        bodyColSizes.value = colSizes;
        tableColumns.value = util$1.getTableColumns(bodyCols.value, bodyColSizes.value);
      }
      if (isUpdate) {
        tableKey.value++;
      }
    };
    const sort = (prop, order) => {
      const col = util$1.getColumnByKey(props2.columns, void 0, prop);
      sortBy.value = {
        key: util$1.getColKey(col),
        order: util$1.getSortOrder(order)
      };
      const sorter = { prop, order, column: col };
      sortAndFilterTableData(sorter);
      events.onSortChange(sorter);
    };
    const scrollTo = (options, yCoord) => {
      if (!tableRef.value) {
        return;
      }
      const isNumber = typeof options === "number";
      const left = isNumber ? options : options.left;
      const top = isNumber ? yCoord : options.top;
      tableRef.value.scrollTo({
        scrollTop: top,
        scrollLeft: left
      });
    };
    const setScrollTop = (top) => {
      if (!tableRef.value) {
        return;
      }
      tableRef.value.scrollToTop(top);
    };
    const setScrollLeft = (left) => {
      if (!tableRef.value) {
        return;
      }
      tableRef.value.scrollToLeft(left);
    };
    const scrollToRow = (row, strategy) => {
      if (!tableRef.value) {
        return;
      }
      tableRef.value.scrollToRow(row, strategy);
    };
    const updateCurrentRowKey = (key) => {
      if (util.valueIsChanged(props2.currentRowKey, key)) {
        events["onUpdate:currentRowKey"](key);
      }
    };
    const updateSelectedRowKeys = (keys) => {
      const selected = props2.selectedRowKeys || [];
      if (util.arrayIsChanged(selected, keys)) {
        events["onUpdate:selectedRowKeys"](keys);
      }
    };
    vue.onActivated(() => {
      const top = tableState.scrollTop;
      const left = tableScrollLeft.value;
      if (top || left) {
        scrollTo(left ? left - 1 : 0, top ? top - 1 : 0);
      }
    });
    vue.onDeactivated(() => {
      hideTooltip();
    });
    vue.watch(
      [
        () => props2.height,
        () => props2.maxHeight,
        tableRowHeight,
        headerNums,
        hasFooter,
        wrapHeight
      ],
      () => {
        const minRows = headerNums.value + (hasFooter.value ? 2 : 1);
        const height = util$1.getTableHeight(
          props2.height,
          props2.maxHeight,
          minRows * tableRowHeight.value,
          wrapHeight.value
        );
        if (height !== tableHeight.value) {
          tableHeight.value = height;
        }
      },
      { immediate: true }
    );
    vue.watch(
      () => props2.columns,
      (columns) => {
        tableState.reserveChecked = util.isReserveChecked(columns);
        const { cols, rows } = util$1.analyseColumns(columns);
        bodyCols.value = cols;
        headerRows.value = rows;
        doLayout(true);
      },
      {
        deep: true,
        immediate: true
      }
    );
    vue.watch(wrapWidth, () => {
      doLayout();
    });
    vue.watch(
      [() => props2.data, hasExpandCol, treeChildrenName],
      () => {
        updateTableData();
      },
      { immediate: true }
    );
    vue.watch(
      () => props2.rowKey,
      () => {
        setCurrentRow();
        clearSelection();
        toggleRowExpansionAll(false);
        updateTableData();
      }
    );
    vue.watch([tableData, () => props2.cacheData], () => {
      updateSelectedAndChecked();
    });
    vue.watch(
      () => props2.currentRowKey,
      (key) => {
        updateSelectedState(key);
      }
    );
    vue.watch(
      () => props2.selectedRowKeys,
      (selectedRowKeys) => {
        setSelectedRowKeys(selectedRowKeys || []);
      },
      { deep: true }
    );
    vue.watch(
      () => props2.expandRowKeys,
      (expandKeys) => {
        if (expandKeys != null) {
          expandedRowKeys.value = [...expandKeys];
        }
      },
      { deep: true }
    );
    vue.watch(
      () => props2.showHeader,
      (showHeader) => {
        if (showHeader) {
          vue.nextTick(() => {
            const left = tableScrollLeft.value;
            if (left) {
              setScrollLeft(left - 1);
            }
          });
        }
      }
    );
    __expose({
      tableRef,
      updateWrapSize,
      updateTableData,
      updateSelectedAndChecked,
      setSelectedRows,
      setSelectedRowKeys,
      toggleRowExpansionAll,
      clearSelection,
      getSelectionRows,
      toggleRowSelection,
      toggleAllSelection,
      toggleRowExpansion,
      setCurrentRow,
      setCurrentRowKey,
      getCurrentRow,
      clearSort,
      clearFilter,
      doLayout,
      sort,
      scrollTo,
      setScrollTop,
      setScrollLeft,
      scrollToRow,
      hideTooltip
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "rootRef",
        ref: rootRef,
        class: vue.normalizeClass(["ele-virtual-table", [
          { "is-border": _ctx.border || headerRows.value.length > 1 },
          { "is-stripe": _ctx.stripe },
          { "is-sticky": _ctx.sticky },
          { "is-layout-fixed-head": _ctx.sticky && vue.unref(isLayoutFixedHead) },
          { "is-layout-maximized": _ctx.sticky && vue.unref(isLayoutMaximized) },
          { "has-footer": hasFooter.value },
          { "hide-header": !_ctx.showHeader },
          { "hide-bottom-line": !_ctx.bottomLine },
          { "is-ping-left": isPingLeft.value },
          { "is-ping-right": isPingRight.value },
          { "is-auto-width": vue.unref(wrapWidth) === tableWidth.value },
          { "is-small": _ctx.size === "small" },
          { "is-large": _ctx.size === "large" }
        ]]),
        onMouseleave: handleTableMouseleave
      }, [
        tableProps.value.width ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTableV2), vue.mergeProps({ key: 0 }, tableProps.value, {
          key: tableKey.value,
          ref_key: "tableRef",
          ref: tableRef,
          onScroll: handleTableScroll,
          onEndEeached: handleEndEeached,
          onRowsRendered: handleRowsRendered
        }), vue.createSlots({
          header: vue.withCtx((headerProps) => [
            headerProps && headerRows.value[headerProps.headerIndex] ? (vue.openBlock(), vue.createBlock(HeaderRow, {
              key: 0,
              headerCols: headerRows.value[headerProps.headerIndex],
              headerColSizes: headerRowSizes.value[headerProps.headerIndex],
              headerIndex: headerProps.headerIndex,
              sortBy: sortBy.value,
              filtered,
              isCheckAll: isCheckAll.value,
              isIndeterminate: isIndeterminate.value,
              disabledCheckbox: !tableData.value.length,
              tableSize: _ctx.size,
              headerCellClass: _ctx.headerCellClassName,
              headerCellStyle: _ctx.headerCellStyle,
              headerEllipsis: true,
              rowHeight: tableRowHeight.value,
              onCheckedChange: _cache[0] || (_cache[0] = ($event) => toggleAllSelection()),
              onFilterChange: handleTableFilterChange,
              onCellClick: handleHeaderCellClick,
              onCellContextmenu: handleHeaderCellContextmenu,
              onCellMouseenter: handleHeaderCellMouseenter
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter(
                (k) => !ownSlots.includes(k)
              ), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["headerCols", "headerColSizes", "headerIndex", "sortBy", "filtered", "isCheckAll", "isIndeterminate", "disabledCheckbox", "tableSize", "headerCellClass", "headerCellStyle", "rowHeight"])) : vue.createCommentVNode("", true)
          ]),
          row: vue.withCtx((rowProps) => [
            rowProps && rowProps.rowData && rowProps.rowData.isExpandRow ? (vue.openBlock(), vue.createBlock(ExpandRow, {
              key: 0,
              column: tableExpandCol.value?.originalCol,
              rowIndex: rowProps.rowData.rowIndex,
              rowData: rowProps.rowData.rowData,
              onMouseenter: handleExpandCellMouseenter
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter(
                (k) => !ownSlots.includes(k)
              ), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["column", "rowIndex", "rowData"])) : rowProps && rowProps.rowData && rowProps.rowData.rowData ? (vue.openBlock(), vue.createBlock(BodyRow, {
              key: 1,
              bodyCols: bodyCols.value,
              colSizes: bodyColSizes.value,
              rowIndex: rowProps.rowData.rowIndex,
              rowItem: rowProps.rowData,
              rowId: rowProps.rowData.rowId,
              checkedRowKeys: checkedRowKeys.value,
              bodyCellClass: _ctx.cellClassName,
              bodyCellStyle: _ctx.cellStyle,
              spanMethod: _ctx.spanMethod,
              tableTooltipProps: _ctx.showOverflowTooltip,
              pageIndex: _ctx.pageIndex,
              rowHeight: tableRowHeight.value,
              tableSize: _ctx.size,
              expandColumnKey: tableExpandColumnKey.value,
              expandedRowKeys: expandedRowKeys.value,
              lazy: _ctx.lazy,
              load: _ctx.load,
              level: rowProps.depth,
              indent: _ctx.indent,
              fixedCellHeight: hasExpandCol.value,
              autoRowHeight: autoRowHeight.value,
              onCellCheckedChange: handleCellCheckedChange,
              onCellExpandChange: handleCellExpandChange,
              onCellClick: handleCellClick,
              onCellDblclick: handleCellDblclick,
              onCellContextmenu: handleCellContextmenu,
              onCellMouseenter: handleCellMouseenter,
              onCellMouseleave: handleCellMouseleave
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter(
                (k) => !ownSlots.includes(k)
              ), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["bodyCols", "colSizes", "rowIndex", "rowItem", "rowId", "checkedRowKeys", "bodyCellClass", "bodyCellStyle", "spanMethod", "tableTooltipProps", "pageIndex", "rowHeight", "tableSize", "expandColumnKey", "expandedRowKeys", "lazy", "load", "level", "indent", "fixedCellHeight", "autoRowHeight"])) : vue.createCommentVNode("", true)
          ]),
          empty: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "empty", {
              text: _ctx.emptyText,
              error: _ctx.errorText
            }, () => [
              _ctx.emptyProps === false ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, vue.toDisplayString(tableEmptyText.value), 1)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElEmpty), vue.mergeProps({
                key: 1,
                imageSize: 68
              }, !_ctx.emptyProps || _ctx.emptyProps === true ? {} : _ctx.emptyProps, {
                description: tableEmptyText.value,
                class: "ele-table-empty"
              }), null, 16, ["description"]))
            ])
          ]),
          _: 2
        }, [
          hasFooter.value ? {
            name: "footer",
            fn: vue.withCtx(() => [
              vue.createVNode(FooterRow, {
                bodyCols: bodyCols.value,
                colSizes: bodyColSizes.value,
                sumWidth: colsSumWidth.value,
                tableData: tableCurrentData.value,
                rowHeight: tableRowHeight.value,
                sumText: tableSumText.value,
                summaryMethod: _ctx.summaryMethod,
                onMouseenter: handleFooterCellMouseenter
              }, null, 8, ["bodyCols", "colSizes", "sumWidth", "tableData", "rowHeight", "sumText", "summaryMethod"])
            ]),
            key: "0"
          } : void 0
        ]), 1040)) : vue.createCommentVNode("", true),
        vue.createVNode(EleTooltip, vue.normalizeProps(vue.guardReactiveProps(tableTooltipProps)), null, 16)
      ], 34);
    };
  }
});
module.exports = _sfc_main;
