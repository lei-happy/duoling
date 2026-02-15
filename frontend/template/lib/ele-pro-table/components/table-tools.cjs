"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const EleDropdown = require("../../ele-dropdown/index");
const util = require("../util");
const EleTool = require("../../ele-tool/index");
const ToolColumn = require("./tool-column");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "table-tools",
  props: {
    /** 工具按钮布局 */
    tools: {
      type: Array,
      required: true
    },
    /** 表格尺寸 */
    size: String,
    /** 表格列数据 */
    columns: Array,
    /** 是否开启列拖拽排序 */
    columnSortable: Boolean,
    /** 是否开启开关固定列 */
    columnFixed: Boolean,
    /** 是否最大化 */
    maximized: Boolean,
    /** 本地缓存的名称 */
    cacheKey: String,
    /** 国际化 */
    lang: {
      type: Object,
      required: true
    }
  },
  emits: {
    reload: () => true,
    "update:size": (_size) => true,
    "update:columns": (_columns, _tableColumns, _isReset) => true,
    "update:maximized": (_maximized) => true,
    openExportModal: () => true,
    openPrintModal: () => true
  },
  setup(__props, { emit: __emit }) {
    const ownSlots = ["default", "printTop", "printBottom"];
    const props = __props;
    const emit = __emit;
    const placement = vue.computed(() => props.maximized ? "bottom" : "top");
    const sizeDropdownItems = vue.computed(() => {
      return [
        {
          title: props.lang.sizeLarge,
          command: "large",
          icon: vue.markRaw(index.SizeSlackOutlined)
        },
        {
          title: props.lang.sizeDefault,
          command: "default",
          icon: vue.markRaw(index.SizeMiddleOutlined)
        },
        {
          title: props.lang.sizeSmall,
          command: "small",
          icon: vue.markRaw(index.SizeCompactOutlined)
        }
      ];
    });
    const reload = () => {
      emit("reload");
    };
    const updateSize = (size) => {
      if (props.cacheKey) {
        localStorage.setItem(util.getSizeCacheKey(props.cacheKey), size);
      }
      emit("update:size", size);
    };
    const updateColumns = (columns, tableColumns, isReset) => {
      emit("update:columns", columns, tableColumns, isReset);
    };
    const toggleMaximized = () => {
      emit("update:maximized", !props.maximized);
    };
    const openExportModal = () => {
      emit("openExportModal");
    };
    const openPrintModal = () => {
      emit("openPrintModal");
    };
    return (_ctx, _cache) => {
      return vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.tools, (tool, index$1) => {
        return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
          tool === "reload" ? (vue.openBlock(), vue.createBlock(EleTool, {
            key: index$1 + "-reload",
            placement: placement.value,
            title: __props.lang.refresh,
            onClick: reload
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.ReloadOutlined))
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["placement", "title"])) : tool === "export" ? (vue.openBlock(), vue.createBlock(EleTool, {
            key: index$1 + "-export",
            title: __props.lang.export,
            placement: placement.value,
            clickHideTooltip: true,
            onClick: openExportModal
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), { style: { transform: "scale(1.1)", transformOrigin: "bottom" } }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.DownloadOutlined))
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["title", "placement"])) : tool === "print" ? (vue.openBlock(), vue.createBlock(EleTool, {
            key: index$1 + "-print",
            title: __props.lang.print,
            placement: placement.value,
            clickHideTooltip: true,
            onClick: openPrintModal
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.PrinterOutlined))
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["title", "placement"])) : tool === "size" ? (vue.openBlock(), vue.createBlock(EleTool, {
            key: index$1 + "-size",
            placement: placement.value,
            title: __props.lang.sizes
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(EleDropdown, {
                trigger: "click",
                placement: "bottom",
                validateEvent: false,
                popperClass: "ele-tool-size-popper",
                modelValue: __props.size,
                items: sizeDropdownItems.value,
                popperOptions: {
                  modifiers: [{ name: "offset", options: { offset: [0, 10] } }]
                },
                onCommand: updateSize
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.ColumnHeightOutlined))
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["modelValue", "items"])
            ]),
            _: 1
          }, 8, ["placement", "title"])) : tool === "columns" ? (vue.openBlock(), vue.createBlock(ToolColumn, {
            key: index$1 + "-columns",
            placement: placement.value,
            locale: __props.lang,
            columns: __props.columns,
            sortable: __props.columnSortable,
            allowFixed: __props.columnFixed,
            cacheKey: __props.cacheKey,
            "onUpdate:columns": updateColumns
          }, null, 8, ["placement", "locale", "columns", "sortable", "allowFixed", "cacheKey"])) : tool === "maximized" ? (vue.openBlock(), vue.createBlock(EleTool, {
            key: index$1 + "-maximized",
            placement: placement.value,
            title: __props.lang.maximized,
            clickHideTooltip: true,
            onClick: toggleMaximized
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                default: vue.withCtx(() => [
                  __props.maximized ? (vue.openBlock(), vue.createBlock(vue.unref(index.FullscreenExitOutlined), { key: 0 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.FullscreenOutlined), { key: 1 }))
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["placement", "title"])) : tool && !ownSlots.includes(tool) && _ctx.$slots[tool] ? vue.renderSlot(_ctx.$slots, tool, { key: 6 }) : vue.createCommentVNode("", true)
        ], 64);
      }), 256);
    };
  }
});
module.exports = _sfc_main;
