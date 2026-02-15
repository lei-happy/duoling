"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../../utils/common");
const EleModal = require("../../ele-modal/index");
const util = require("../util");
const ToolColumnList = require("./tool-column-list");
const _hoisted_1 = { class: "ele-tool-column is-sortable" };
const _hoisted_2 = { class: "ele-tool-column-header" };
const _hoisted_3 = { class: "ele-tool-column-label" };
const _hoisted_4 = { class: "ele-tool-form-options" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "tool-export",
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
    /** 序号列起始索引 */
    pageIndex: Number,
    /** 树表字段名 */
    treeProps: Object,
    /** 表格请求数据方法 */
    fetch: Function,
    /** 默认文件名 */
    defaultFileName: {
      type: String,
      default: "list"
    },
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
    /** 导出前的钩子函数 */
    beforeExport: Function,
    /** 导出插件 */
    exportPlugin: Function,
    /** 获取数据源返回结果方法 */
    getDatasourceResult: {
      type: Function,
      required: true
    }
  },
  setup(__props, { expose: __expose }) {
    const props = __props;
    const visible = vue.ref(false);
    const loading = vue.ref(false);
    const formRef = vue.ref(null);
    const form = vue.reactive({
      /** 文件名 */
      fileName: props.defaultFileName
    });
    const fileNameRules = vue.reactive({
      required: true,
      message: props.locale.exportFileNamePlaceholder,
      type: "string",
      trigger: "blur"
    });
    const dataType = vue.ref(props.defaultDataType);
    const colItems = vue.ref([]);
    const isCheckAll = vue.ref(false);
    const isIndeterminate = vue.ref(false);
    const showHeader = vue.ref(true);
    const showFooter = vue.ref(false);
    const showTreeIndex = vue.ref(false);
    const treeIndexDisabled = vue.ref(true);
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
    const exportData = (params) => {
      showLoading();
      const exportFileName = params?.fileName ?? form.fileName;
      const exportDataValue = params?.data || [];
      const isShowHeader = params?.showHeader ?? showHeader.value;
      const isShowFooter = params?.showFooter ?? showFooter.value;
      const isShowTreeIndex = params?.showTreeIndex ?? showTreeIndex.value;
      const exportDataType = params?.dataType ?? dataType.value;
      const exportColumns = params?.columns || util.getCheckedColumns(
        props.columns,
        colItems.value,
        true,
        void 0,
        util.columnsExportFilter,
        false,
        colItems.value
      );
      const tableColumns = params?.tableColumns || params?.columns || util.getCheckedColumns(
        props.columns,
        colItems.value,
        true,
        void 0,
        util.columnsExportFilter,
        true,
        colItems.value
      );
      const { headerData, bodyData, footerData, bodyCols } = util.getExportData(
        exportDataValue,
        exportColumns,
        props.spanMethod,
        exportDataType === "pageData" ? props.pageIndex : void 0,
        isShowFooter,
        props.sumText,
        props.summaryMethod,
        props.treeProps?.children,
        isShowTreeIndex,
        isShowHeader
      );
      const exportParams = {
        data: exportDataValue,
        columns: exportColumns,
        headerData,
        bodyData,
        footerData,
        bodyCols,
        fileName: exportFileName,
        dataType: exportDataType,
        hideLoading,
        closeModal,
        showHeader: isShowHeader,
        showFooter: isShowFooter,
        showTreeIndex: isShowTreeIndex,
        tableColumns
      };
      if (typeof props.beforeExport === "function") {
        const flag = props.beforeExport(exportParams);
        if (flag === false) {
          return;
        }
      }
      if (props.exportPlugin == null) {
        util.exportCSV(exportFileName, headerData, bodyData, footerData);
        hideLoading();
        closeModal();
        return;
      }
      props.exportPlugin(exportParams).then(() => {
        hideLoading();
        closeModal();
      }).catch(() => {
        hideLoading();
      });
    };
    const handleExport = () => {
      formRef.value?.validate?.((valid) => {
        if (!valid) {
          return;
        }
        if (dataType.value === "selections") {
          exportData({ data: [...props.selections || []] });
          return;
        }
        if (dataType.value !== "data") {
          exportData({ data: [...props.pageData || []] });
          return;
        }
        if (props.datasource == null || typeof props.datasource !== "function" || typeof props.fetch !== "function") {
          return;
        }
        const columns = util.getCheckedColumns(
          props.columns,
          colItems.value,
          true,
          void 0,
          util.columnsExportFilter,
          false,
          colItems.value
        );
        const tableColumns = util.getCheckedColumns(
          props.columns,
          colItems.value,
          true,
          void 0,
          util.columnsExportFilter,
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
              exportData({ data: result });
              return;
            }
            const { data } = props.getDatasourceResult(result);
            if (data == null) {
              hideLoading();
              closeModal();
              return;
            }
            exportData({ data });
          }).catch((e) => {
            console.error(e);
            hideLoading();
          });
        });
      });
    };
    const initColItems = () => {
      const colsWidth = util.getCacheColsWidth(props.cacheKey);
      const { cols, checkAll, indeterminate } = util.getColItems(
        props.columns,
        props.locale,
        util.columnsExportFilter,
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
        form.fileName = props.defaultFileName;
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
      hideLoading();
      formRef.value?.clearValidate?.();
    });
    vue.watch(
      () => props.locale.exportFileNamePlaceholder,
      (placeholder) => {
        fileNameRules.message = placeholder;
      }
    );
    __expose({
      openModal,
      closeModal,
      exportData
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, vue.mergeProps({
        form: true,
        width: "460px",
        title: __props.locale.export,
        position: "center"
      }, __props.modalProps || {}, {
        modelValue: visible.value,
        "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => visible.value = $event)
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
            onClick: handleExport
          }, {
            default: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(__props.locale.exportOk), 1)
            ]),
            _: 1
          }, 8, ["loading"])
        ]),
        default: vue.withCtx(() => [
          vue.createVNode(vue.unref(elementPlus.ElForm), {
            ref_key: "formRef",
            ref: formRef,
            model: form,
            labelWidth: "80px",
            onSubmit: _cache[5] || (_cache[5] = vue.withModifiers(() => {
            }, ["prevent"])),
            class: "ele-tool-export-form"
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElFormItem), {
                label: __props.locale.exportFileName,
                prop: "fileName",
                rules: fileNameRules
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(elementPlus.ElInput), {
                    maxlength: 200,
                    clearable: true,
                    modelValue: form.fileName,
                    "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => form.fileName = $event),
                    placeholder: __props.locale.exportFileNamePlaceholder
                  }, null, 8, ["modelValue", "placeholder"])
                ]),
                _: 1
              }, 8, ["label", "rules"]),
              vue.createVNode(vue.unref(elementPlus.ElFormItem), {
                label: __props.locale.exportSelectData
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(elementPlus.ElSelect), {
                    modelValue: dataType.value,
                    "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => dataType.value = $event),
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
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => showHeader.value = $event)
                    }, null, 8, ["label", "modelValue"]),
                    vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                      label: __props.locale.exportOtherFooter,
                      modelValue: showFooter.value,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => showFooter.value = $event),
                      disabled: !__props.showSummary
                    }, null, 8, ["label", "modelValue", "disabled"]),
                    vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                      label: __props.locale.exportOtherTreeIndex,
                      modelValue: showTreeIndex.value,
                      "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => showTreeIndex.value = $event),
                      disabled: treeIndexDisabled.value,
                      onChange: handleTreeIndexChange
                    }, null, 8, ["label", "modelValue", "disabled"])
                  ])
                ]),
                _: 1
              }, 8, ["label"])
            ]),
            _: 1
          }, 8, ["model"])
        ]),
        _: 1
      }, 16, ["title", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
