"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../../utils/common");
const EleModal = require("../../ele-modal/index");
const ElePrinter = require("../../ele-printer/index");
const EleTable = require("../../ele-table/index");
const util = require("../../ele-virtual-table/util");
const util$1 = require("../util");
const ToolColumnList = require("./tool-column-list");
const ToolPrintBodyCell = require("./tool-print-body-cell");
const ToolPrintHeaderCell = require("./tool-print-header-cell");
const _hoisted_1 = { class: "ele-tool-column is-sortable" };
const _hoisted_2 = { class: "ele-tool-column-header" };
const _hoisted_3 = { class: "ele-tool-column-label" };
const _hoisted_4 = { class: "ele-tool-form-options" };
const _hoisted_5 = ["width"];
const _hoisted_6 = { key: 0 };
const _hoisted_7 = ["colspan", "rowspan"];
const _hoisted_8 = ["rowspan", "colspan"];
const _hoisted_9 = ["colspan", "rowspan"];
const _hoisted_10 = { key: 1 };
const _hoisted_11 = ["colspan", "rowspan"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ToolPrint" },
  __name: "tool-print",
  props: {
    /** 表格国际化 */
    locale: {
      type: Object,
      required: true
    },
    /** 缓存本地的名称 */
    cacheKey: String,
    /** 弹窗参数 */
    modalProps: Object,
    /** 打印组件参数 */
    printerProps: Object,
    /** 打印表格参数 */
    tableProps: Object,
    /** 列数据 */
    columns: Array,
    /** 表格选中数据 */
    selections: Array,
    /** 表格当前页数据 */
    pageData: Array,
    /** 表格全部数据 */
    datasource: [Array, Function],
    /** 单元格合并行列方法 */
    spanMethod: Function,
    /** 表格是否有表头 */
    tableHeader: Boolean,
    /** 是否显示合计行 */
    showSummary: Boolean,
    /** 合计行文本 */
    sumText: String,
    /** 合计行自定义方法 */
    summaryMethod: Function,
    /** 自定义表格样式 */
    tableStyle: Object,
    /** 单元格样式 */
    cellStyle: [Object, Function],
    /** 单元格类名自定义 */
    cellClassName: [String, Function],
    /** 单元格样式 */
    headerCellStyle: [Object, Function],
    /** 单元格类名自定义 */
    headerCellClassName: [String, Function],
    /** 序号列起始索引 */
    pageIndex: Number,
    /** 树表字段名 */
    treeProps: Object,
    /** 表格请求数据方法 */
    fetch: Function,
    /** 默认数据类型 */
    defaultDataType: {
      type: String,
      default: "pageData"
    },
    /** 默认是否勾选表尾 */
    defaultShowFooter: {
      type: Boolean,
      default: true
    },
    /** 默认是否勾选层级序号 */
    defaultShowTreeIndex: Boolean,
    /** 打印前的钩子函数 */
    beforePrint: Function,
    /** 打印插件 */
    printPlugin: Function,
    /** 获取数据源返回结果方法 */
    getDatasourceResult: {
      type: Function,
      required: true
    }
  },
  setup(__props, { expose: __expose }) {
    const ownSlots = ["printTop", "printBottom"];
    const props = __props;
    const visible = vue.ref(false);
    const loading = vue.ref(false);
    const dataType = vue.ref(props.defaultDataType);
    const colItems = vue.ref([]);
    const isCheckAll = vue.ref(false);
    const isIndeterminate = vue.ref(false);
    const showHeader = vue.ref(true);
    const showFooter = vue.ref(false);
    const showTreeIndex = vue.ref(false);
    const treeIndexDisabled = vue.ref(true);
    const printOptions = vue.reactive({
      printing: false,
      headerData: [],
      bodyData: [],
      footerData: [],
      hasHeader: false,
      hasFooter: false,
      bodyCols: [],
      data: []
    });
    const showLoading = () => {
      loading.value = true;
    };
    const hideLoading = () => {
      loading.value = false;
    };
    const openModal = () => {
      visible.value = true;
    };
    const closeModal = () => {
      hideLoading();
      visible.value = false;
    };
    const handlePrintDone = () => {
      hideLoading();
    };
    const printData = (params) => {
      showLoading();
      const printDataValue = params?.data || [];
      const isShowHeader = params?.showHeader ?? showHeader.value;
      const isShowFooter = params?.showFooter ?? showFooter.value;
      const isShowTreeIndex = params?.showTreeIndex ?? showTreeIndex.value;
      const printDataType = params?.dataType ?? dataType.value;
      const printColumns = params?.columns || util$1.getCheckedColumns(
        props.columns,
        colItems.value,
        true,
        void 0,
        util$1.columnsPrintFilter,
        false,
        colItems.value
      );
      const tableColumns = params?.tableColumns || params?.columns || util$1.getCheckedColumns(
        props.columns,
        colItems.value,
        true,
        void 0,
        util$1.columnsPrintFilter,
        true,
        colItems.value
      );
      const { headerData, bodyData, footerData, bodyCols } = util$1.getExportData(
        printDataValue,
        printColumns,
        props.spanMethod,
        printDataType === "pageData" ? props.pageIndex : void 0,
        isShowFooter,
        props.sumText,
        props.summaryMethod,
        props.treeProps?.children,
        isShowTreeIndex,
        isShowHeader
      );
      const printParams = {
        data: printDataValue,
        columns: printColumns,
        headerData,
        bodyData,
        footerData,
        bodyCols,
        dataType: printDataType,
        hideLoading,
        closeModal,
        showHeader: isShowHeader,
        showFooter: isShowFooter,
        showTreeIndex: isShowTreeIndex,
        tableColumns
      };
      if (typeof props.beforePrint === "function") {
        const flag = props.beforePrint(printParams);
        if (flag === false) {
          return;
        }
      }
      if (props.printPlugin == null) {
        printOptions.data = printDataValue;
        printOptions.headerData = headerData;
        printOptions.bodyData = bodyData;
        printOptions.footerData = footerData;
        printOptions.hasHeader = !!printOptions.headerData.length;
        printOptions.hasFooter = !!printOptions.footerData.length;
        printOptions.bodyCols = bodyCols;
        vue.nextTick(() => {
          printOptions.printing = true;
        });
        return;
      }
      props.printPlugin(printParams).then(() => {
        hideLoading();
        closeModal();
      }).catch(() => {
        hideLoading();
      });
    };
    const handlePrint = () => {
      if (dataType.value === "selections") {
        printData({ data: [...props.selections || []] });
        return;
      }
      if (dataType.value !== "data") {
        printData({ data: [...props.pageData || []] });
        return;
      }
      if (props.datasource == null || typeof props.datasource !== "function" || typeof props.fetch !== "function") {
        return;
      }
      const columns = util$1.getCheckedColumns(
        props.columns,
        colItems.value,
        true,
        void 0,
        util$1.columnsPrintFilter,
        false,
        colItems.value
      );
      const tableColumns = util$1.getCheckedColumns(
        props.columns,
        colItems.value,
        true,
        void 0,
        util$1.columnsPrintFilter,
        true,
        colItems.value
      );
      showLoading();
      props.fetch((params) => {
        props.datasource({
          ...params,
          columns,
          tableColumns
        }).then((result) => {
          if (result == null) {
            hideLoading();
            closeModal();
            return;
          }
          if (Array.isArray(result)) {
            printData({ data: result });
            return;
          }
          const { data } = props.getDatasourceResult(result);
          if (data == null) {
            hideLoading();
            closeModal();
            return;
          }
          printData({ data });
        }).catch((e) => {
          console.error(e);
          hideLoading();
        });
      });
    };
    const initColItems = () => {
      const colsWidth = util$1.getCacheColsWidth(props.cacheKey);
      const { cols, checkAll, indeterminate } = util$1.getColItems(
        props.columns,
        props.locale,
        util$1.columnsPrintFilter,
        void 0,
        true,
        true,
        colsWidth
      );
      colItems.value = cols;
      isCheckAll.value = checkAll;
      isIndeterminate.value = indeterminate;
    };
    const handleCheckedChange = (item, checked, type) => {
      let checkAll = true;
      let indeterminate = false;
      common.eachTree(colItems.value, (d) => {
        const flag = item == null ? type === d.type : d.uid === item.uid;
        if (flag) {
          d.checked = checked;
        }
        if (!d.checked && checkAll) {
          checkAll = false;
        }
        if (d.checked && !indeterminate) {
          indeterminate = true;
        }
        if (flag && !checkAll && indeterminate) {
          return false;
        }
      });
      isCheckAll.value = colItems.value.length > 0 && checkAll;
      isIndeterminate.value = !checkAll && indeterminate;
    };
    const handleCheckAllChange = (checked) => {
      isCheckAll.value = checked;
      isIndeterminate.value = false;
      common.eachTree(colItems.value, (d) => {
        if (d.checked !== checked) {
          d.checked = checked;
        }
      });
    };
    const handleSortChange = (items, parent) => {
      if (!parent) {
        colItems.value = items;
      } else {
        common.eachTree(colItems.value, (d) => {
          if (d.uid === parent.uid) {
            d.children = items;
            return false;
          }
        });
      }
    };
    const handleColWidthChange = (item, width) => {
      common.eachTree(colItems.value, (d) => {
        if (d.uid === item.uid) {
          d.width = width;
          return false;
        }
      });
    };
    const handleReset = () => {
      initColItems();
    };
    const handleTreeIndexChange = (checked) => {
      if (checked) {
        handleCheckedChange(void 0, false, "index");
      }
    };
    vue.watch(visible, (visible2) => {
      if (visible2) {
        dataType.value = props.defaultDataType;
        initColItems();
        showHeader.value = !!props.tableHeader;
        showFooter.value = props.showSummary ? !!props.defaultShowFooter : false;
        treeIndexDisabled.value = !(props.pageData && props.pageData.some(
          (d) => d[props.treeProps?.children || "children"]?.length || d[props.treeProps?.hasChildren || "hasChildren"]
        )) && common.findTree(colItems.value, (c) => c.type === "expand") == null;
        showTreeIndex.value = treeIndexDisabled.value ? false : !!props.defaultShowTreeIndex;
        return;
      }
      printOptions.data = [];
      printOptions.headerData = [];
      printOptions.bodyData = [];
      printOptions.footerData = [];
      printOptions.bodyCols = [];
      printOptions.hasHeader = false;
      printOptions.hasFooter = false;
      printOptions.printing = false;
      hideLoading();
    });
    __expose({
      openModal,
      closeModal,
      printData
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createVNode(EleModal, vue.mergeProps({
          form: true,
          width: "460px",
          title: __props.locale.print,
          position: "center"
        }, __props.modalProps || {}, {
          modelValue: visible.value,
          "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => visible.value = $event)
        }), {
          footer: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElButton), { onClick: closeModal }, {
              default: vue.withCtx(() => [
                vue.createTextVNode(vue.toDisplayString(__props.locale.exportCancel), 1)
              ]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElButton), {
              loading: loading.value,
              type: "primary",
              onClick: handlePrint
            }, {
              default: vue.withCtx(() => [
                vue.createTextVNode(vue.toDisplayString(__props.locale.exportOk), 1)
              ]),
              _: 1
            }, 8, ["loading"])
          ]),
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElForm), {
              labelWidth: "80px",
              onSubmit: _cache[4] || (_cache[4] = vue.withModifiers(() => {
              }, ["prevent"])),
              class: "ele-tool-print-form"
            }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(elementPlus.ElFormItem), {
                  label: __props.locale.exportSelectData
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(elementPlus.ElSelect), {
                      modelValue: dataType.value,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => dataType.value = $event),
                      placeholder: __props.locale.exportSelectData
                    }, {
                      default: vue.withCtx(() => [
                        __props.pageData != null ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElOption), {
                          key: 0,
                          value: "pageData",
                          label: __props.locale.exportDataTypePage
                        }, null, 8, ["label"])) : vue.createCommentVNode("", true),
                        __props.selections != null ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElOption), {
                          key: 1,
                          value: "selections",
                          label: __props.locale.exportDataTypeSelected
                        }, null, 8, ["label"])) : vue.createCommentVNode("", true),
                        __props.datasource != null ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElOption), {
                          key: 2,
                          value: "data",
                          label: __props.locale.exportDataTypeAll
                        }, null, 8, ["label"])) : vue.createCommentVNode("", true)
                      ]),
                      _: 1
                    }, 8, ["modelValue", "placeholder"])
                  ]),
                  _: 1
                }, 8, ["label"]),
                vue.createVNode(vue.unref(elementPlus.ElFormItem), {
                  label: __props.locale.exportSelectColumn
                }, {
                  default: vue.withCtx(() => [
                    vue.createElementVNode("div", _hoisted_1, [
                      vue.createElementVNode("div", _hoisted_2, [
                        vue.createElementVNode("div", _hoisted_3, [
                          vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                            label: __props.locale.columnTitle,
                            modelValue: isCheckAll.value,
                            indeterminate: isIndeterminate.value,
                            "onUpdate:modelValue": handleCheckAllChange
                          }, null, 8, ["label", "modelValue", "indeterminate"])
                        ]),
                        vue.createElementVNode("div", {
                          class: "ele-tool-column-link",
                          onClick: handleReset
                        }, vue.toDisplayString(__props.locale.columnReset), 1)
                      ]),
                      vue.createVNode(ToolColumnList, {
                        data: colItems.value,
                        sortable: true,
                        allowWidth: true,
                        columnWidthPlaceholder: __props.locale.columnWidth,
                        onSortChange: handleSortChange,
                        onCheckedChange: handleCheckedChange,
                        onColWidthChange: handleColWidthChange
                      }, null, 8, ["data", "columnWidthPlaceholder"])
                    ])
                  ]),
                  _: 1
                }, 8, ["label"]),
                vue.createVNode(vue.unref(elementPlus.ElFormItem), {
                  label: __props.locale.exportOther
                }, {
                  default: vue.withCtx(() => [
                    vue.createElementVNode("div", _hoisted_4, [
                      vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                        label: __props.locale.exportOtherHeader,
                        modelValue: showHeader.value,
                        "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => showHeader.value = $event)
                      }, null, 8, ["label", "modelValue"]),
                      vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                        label: __props.locale.exportOtherFooter,
                        modelValue: showFooter.value,
                        "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => showFooter.value = $event),
                        disabled: !__props.showSummary
                      }, null, 8, ["label", "modelValue", "disabled"]),
                      vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                        label: __props.locale.exportOtherTreeIndex,
                        modelValue: showTreeIndex.value,
                        "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => showTreeIndex.value = $event),
                        disabled: treeIndexDisabled.value,
                        onChange: handleTreeIndexChange
                      }, null, 8, ["label", "modelValue", "disabled"])
                    ])
                  ]),
                  _: 1
                }, 8, ["label"])
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 16, ["title", "modelValue"]),
        vue.createVNode(ElePrinter, vue.mergeProps({ target: "_iframe" }, __props.printerProps || {}, {
          modelValue: printOptions.printing,
          "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => printOptions.printing = $event),
          onDone: handlePrintDone
        }), {
          default: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "printTop", {
              data: printOptions.data
            }),
            vue.createVNode(EleTable, vue.mergeProps({
              border: true,
              printSkin: true,
              hasHeader: printOptions.hasHeader,
              hasFooter: printOptions.hasFooter,
              style: __props.tableStyle
            }, __props.tableProps || {}), {
              default: vue.withCtx(() => [
                vue.createElementVNode("colgroup", null, [
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(printOptions.bodyCols, (col) => {
                    return vue.openBlock(), vue.createElementBlock("col", {
                      key: col.key,
                      width: col.width
                    }, null, 8, _hoisted_5);
                  }), 128))
                ]),
                printOptions.hasHeader ? (vue.openBlock(), vue.createElementBlock("thead", _hoisted_6, [
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(printOptions.headerData, (item, index) => {
                    return vue.openBlock(), vue.createElementBlock("tr", { key: index }, [
                      (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(item, (col, columnIndex) => {
                        return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
                          key: col.key
                        }, [
                          col.isTreeIndex ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                            col.rowspan !== 0 && col.colspan !== 0 ? (vue.openBlock(), vue.createElementBlock("th", {
                              key: 0,
                              colspan: col.colspan,
                              rowspan: col.rowspan,
                              class: "ele-print-tree-index"
                            }, null, 8, _hoisted_7)) : vue.createCommentVNode("", true)
                          ], 64)) : col.rowspan !== 0 && col.colspan !== 0 ? (vue.openBlock(), vue.createBlock(ToolPrintHeaderCell, {
                            key: 1,
                            col,
                            columnIndex,
                            headerCellStyle: __props.headerCellStyle,
                            headerCellClass: __props.headerCellClassName
                          }, vue.createSlots({ _: 2 }, [
                            vue.renderList(Object.keys(_ctx.$slots).filter(
                              (k) => !ownSlots.includes(k)
                            ), (name) => {
                              return {
                                name,
                                fn: vue.withCtx((slotProps) => [
                                  vue.renderSlot(_ctx.$slots, name, vue.mergeProps({ ref_for: true }, slotProps || {}))
                                ])
                              };
                            })
                          ]), 1032, ["col", "columnIndex", "headerCellStyle", "headerCellClass"])) : vue.createCommentVNode("", true)
                        ], 64);
                      }), 128))
                    ]);
                  }), 128))
                ])) : vue.createCommentVNode("", true),
                vue.createElementVNode("tbody", null, [
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(printOptions.bodyData, (item, index) => {
                    return vue.openBlock(), vue.createElementBlock("tr", { key: index }, [
                      (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(item, (col, columnIndex) => {
                        return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
                          key: col.key
                        }, [
                          col.isExpandCell ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                            col.rowspan !== 0 && col.colspan !== 0 ? (vue.openBlock(), vue.createElementBlock("td", {
                              key: 0,
                              rowspan: col.rowspan,
                              colspan: col.colspan,
                              style: { paddingLeft: 0, paddingRight: 0 },
                              class: "ele-print-expand-td"
                            }, [
                              col.column && (col.column.printSlot || col.column.slot) && !ownSlots.includes(
                                col.column.printSlot || col.column.slot
                              ) ? vue.renderSlot(_ctx.$slots, col.column.printSlot || col.column.slot, vue.mergeProps({
                                key: 0,
                                ref_for: true
                              }, {
                                row: col.row,
                                column: col.column,
                                $index: col.index
                              })) : vue.createCommentVNode("", true)
                            ], 8, _hoisted_8)) : vue.createCommentVNode("", true)
                          ], 64)) : col.isTreeIndex ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                            col.rowspan !== 0 && col.colspan !== 0 ? (vue.openBlock(), vue.createElementBlock("td", {
                              key: 0,
                              colspan: col.colspan,
                              rowspan: col.rowspan,
                              style: vue.normalizeStyle({
                                paddingLeft: 0,
                                paddingRight: 0,
                                textAlign: "center",
                                verticalAlign: "top",
                                borderLeftColor: col.hideLeftBorder ? "transparent" : void 0
                              }),
                              class: vue.normalizeClass(["ele-print-tree-index", {
                                "is-placeholder": col.text == null || col.text === ""
                              }])
                            }, vue.toDisplayString(col.text), 15, _hoisted_9)) : vue.createCommentVNode("", true)
                          ], 64)) : col.rowspan !== 0 && col.colspan !== 0 ? (vue.openBlock(), vue.createBlock(ToolPrintBodyCell, {
                            key: 2,
                            col,
                            columnIndex,
                            bodyCellStyle: __props.cellStyle,
                            bodyCellClass: __props.cellClassName
                          }, vue.createSlots({ _: 2 }, [
                            vue.renderList(Object.keys(_ctx.$slots).filter(
                              (k) => !ownSlots.includes(k)
                            ), (name) => {
                              return {
                                name,
                                fn: vue.withCtx((slotProps) => [
                                  vue.renderSlot(_ctx.$slots, name, vue.mergeProps({ ref_for: true }, slotProps || {}))
                                ])
                              };
                            })
                          ]), 1032, ["col", "columnIndex", "bodyCellStyle", "bodyCellClass"])) : vue.createCommentVNode("", true)
                        ], 64);
                      }), 128))
                    ]);
                  }), 128))
                ]),
                printOptions.hasFooter ? (vue.openBlock(), vue.createElementBlock("tfoot", _hoisted_10, [
                  (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(printOptions.footerData, (item, index) => {
                    return vue.openBlock(), vue.createElementBlock("tr", { key: index }, [
                      (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(item, (col) => {
                        return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
                          col.rowspan !== 0 && col.colspan !== 0 ? (vue.openBlock(), vue.createElementBlock("td", {
                            key: col.key,
                            colspan: col.colspan,
                            rowspan: col.rowspan
                          }, [
                            !col.isExpandCell ? (vue.openBlock(), vue.createBlock(vue.unref(util.CellRender), {
                              key: 0,
                              render: () => col.text,
                              params: []
                            }, null, 8, ["render"])) : vue.createCommentVNode("", true)
                          ], 8, _hoisted_11)) : vue.createCommentVNode("", true)
                        ], 64);
                      }), 256))
                    ]);
                  }), 128))
                ])) : vue.createCommentVNode("", true)
              ]),
              _: 3
            }, 16, ["hasHeader", "hasFooter", "style"]),
            vue.renderSlot(_ctx.$slots, "printBottom", {
              data: printOptions.data
            })
          ]),
          _: 3
        }, 16, ["modelValue"])
      ], 64);
    };
  }
});
module.exports = _sfc_main;
