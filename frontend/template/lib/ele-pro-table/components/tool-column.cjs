"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const common = require("../../utils/common");
const EleTooltip = require("../../ele-tooltip/index");
const EleTool = require("../../ele-tool/index");
const util = require("../util");
const ToolColumnList = require("./tool-column-list");
const _hoisted_1 = { class: "ele-tool-column-header" };
const _hoisted_2 = { class: "ele-tool-column-label" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ToolColumn" },
  __name: "tool-column",
  props: {
    /** 提示位置 */
    placement: String,
    /** 表格国际化 */
    locale: {
      type: Object,
      required: true
    },
    /** 列数据 */
    columns: Array,
    /** 是否开启列拖拽排序 */
    sortable: Boolean,
    /** 是否开启开关固定列 */
    allowFixed: Boolean,
    /** 列配置缓存本地的名称 */
    cacheKey: String
  },
  emits: {
    "update:columns": (_columns, _tableColumns, _isReset) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const toolRef = vue.ref(null);
    const colItems = vue.ref([]);
    const isCheckAll = vue.ref(false);
    const isIndeterminate = vue.ref(false);
    const initColItems = () => {
      const { cols, checkAll, indeterminate } = util.getColItems(
        props.columns,
        props.locale,
        util.columnsSettingFilter,
        util.getCacheCols(util.getColsCacheKey(props.cacheKey))
      );
      colItems.value = cols;
      isCheckAll.value = checkAll;
      isIndeterminate.value = indeterminate;
    };
    const updateColumns = (isReset) => {
      const colsWidth = util.getCacheColsWidth(props.cacheKey);
      const columns = util.getCheckedColumns(
        props.columns,
        colItems.value,
        props.sortable,
        (item) => item.hideInSetting,
        void 0,
        false,
        colsWidth
      );
      const tableColumns = util.getCheckedColumns(
        props.columns,
        colItems.value,
        props.sortable,
        (item) => item.hideInSetting,
        void 0,
        true,
        colsWidth
      );
      emit("update:columns", columns, tableColumns, !!isReset);
    };
    const cacheSettingCols = () => {
      if (props.cacheKey) {
        localStorage.setItem(
          util.getColsCacheKey(props.cacheKey),
          JSON.stringify(colItems.value)
        );
      }
    };
    const cleanSettingCols = () => {
      if (props.cacheKey) {
        localStorage.removeItem(util.getColsCacheKey(props.cacheKey));
      }
    };
    const handleCheckedChange = (item, checked) => {
      let checkAll = true;
      let indeterminate = false;
      common.eachTree(colItems.value, (d) => {
        if (d.uid === item.uid) {
          d.checked = checked;
        }
        if (!d.checked && checkAll) {
          checkAll = false;
        }
        if (d.checked && !indeterminate) {
          indeterminate = true;
        }
        if (d.uid === item.uid && !checkAll && indeterminate) {
          return false;
        }
      });
      isCheckAll.value = colItems.value.length > 0 && checkAll;
      isIndeterminate.value = !checkAll && indeterminate;
      cacheSettingCols();
      updateColumns();
    };
    const handleCheckAllChange = (checked) => {
      isCheckAll.value = checked;
      isIndeterminate.value = false;
      common.eachTree(colItems.value, (d) => {
        if (d.checked !== checked) {
          d.checked = checked;
        }
      });
      cacheSettingCols();
      updateColumns();
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
      cacheSettingCols();
      updateColumns();
    };
    const handleFixedLeft = (colItem) => {
      common.eachTree(colItems.value, (d) => {
        if (d.uid === colItem.uid) {
          d.fixed = d.fixed === true || d.fixed === "left" ? false : "left";
          return false;
        }
      });
      cacheSettingCols();
      updateColumns();
    };
    const handleFixedRight = (colItem) => {
      common.eachTree(colItems.value, (d) => {
        if (d.uid === colItem.uid) {
          d.fixed = d.fixed === "right" ? false : "right";
          return false;
        }
      });
      cacheSettingCols();
      updateColumns();
    };
    const handleFixedLeftTooltip = (el) => {
      toolRef.value && toolRef.value.showTooltip(props.locale.columnFixedLeft ?? "", el);
    };
    const handleFixedRightTooltip = (el) => {
      toolRef.value && toolRef.value.showTooltip(props.locale.columnFixedRight ?? "", el);
    };
    const handleReset = () => {
      cleanSettingCols();
      initColItems();
      updateColumns(true);
    };
    vue.watch(
      [() => props.columns, () => props.locale],
      () => {
        initColItems();
      },
      { immediate: true, deep: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleTool, {
        ref_key: "toolRef",
        ref: toolRef,
        title: __props.locale.columns,
        placement: __props.placement,
        clickHideTooltip: true
      }, {
        default: vue.withCtx(() => [
          vue.createVNode(EleTooltip, {
            trigger: "click",
            placement: "bottom-end",
            popperClass: "ele-tool-column-popover",
            transition: "el-zoom-in-top",
            gpuAcceleration: false,
            effect: "light",
            isPopover: true,
            popperOptions: {
              strategy: "fixed",
              modifiers: [{ name: "offset", options: { offset: [20, 10] } }]
            }
          }, {
            body: vue.withCtx(() => [
              vue.createElementVNode("div", {
                class: vue.normalizeClass(["ele-popover-body ele-tool-column", { "is-sortable": __props.sortable }])
              }, [
                vue.createElementVNode("div", _hoisted_1, [
                  vue.createElementVNode("div", _hoisted_2, [
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
                colItems.value.length ? (vue.openBlock(), vue.createBlock(ToolColumnList, {
                  key: 0,
                  data: colItems.value,
                  sortable: __props.sortable,
                  allowFixed: __props.allowFixed,
                  onSortChange: handleSortChange,
                  onCheckedChange: handleCheckedChange,
                  onFixedLeft: handleFixedLeft,
                  onFixedRight: handleFixedRight,
                  onFixedLeftTooltip: handleFixedLeftTooltip,
                  onFixedRightTooltip: handleFixedRightTooltip
                }, null, 8, ["data", "sortable", "allowFixed"])) : vue.createCommentVNode("", true)
              ], 2)
            ]),
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.SettingOutlined))
                ]),
                _: 1
              })
            ]),
            _: 1
          })
        ]),
        _: 1
      }, 8, ["title", "placement"]);
    };
  }
});
module.exports = _sfc_main;
