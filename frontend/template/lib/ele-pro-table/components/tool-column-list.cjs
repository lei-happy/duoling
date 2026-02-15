"use strict";
const vue = require("vue");
const VueDraggable = require("vuedraggable");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const hook = require("../../utils/hook");
const _hoisted_1 = { class: "ele-tool-column-item" };
const _hoisted_2 = { class: "ele-tool-column-item-body" };
const _hoisted_3 = {
  key: 0,
  class: "ele-tool-column-handle"
};
const _hoisted_4 = { class: "ele-tool-column-label" };
const _hoisted_5 = {
  key: 1,
  class: "ele-tool-column-fixed"
};
const _hoisted_6 = ["onClick"];
const _hoisted_7 = ["onClick"];
const _hoisted_8 = {
  key: 2,
  class: "ele-tool-column-input"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ToolColumnList" },
  __name: "tool-column-list",
  props: {
    /** 列配置数据 */
    data: Array,
    /** 父级数据 */
    parent: Object,
    /** 是否开启列拖拽排序 */
    sortable: Boolean,
    /** 是否开启开关固定列 */
    allowFixed: Boolean,
    /** 是否开启列宽设置 */
    allowWidth: Boolean,
    /** 列宽输入框提示文本 */
    columnWidthPlaceholder: String
  },
  emits: {
    sortChange: (_colItems, _parent) => true,
    checkedChange: (_item, _checked) => true,
    fixedLeft: (_item) => true,
    fixedRight: (_item) => true,
    fixedLeftTooltip: (_el) => true,
    fixedRightTooltip: (_el) => true,
    colWidthChange: (_item, _width) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const modalItem = vue.inject(hook.modalItemContextKey, null);
    const handleChildFixedLeftTooltip = (el) => {
      emit("fixedLeftTooltip", el);
    };
    const handleChildFixedRightTooltip = (el) => {
      emit("fixedRightTooltip", el);
    };
    const handleFixedLeftTooltip = (e) => {
      handleChildFixedLeftTooltip(e.currentTarget);
    };
    const handleFixedRightTooltip = (e) => {
      handleChildFixedRightTooltip(e.currentTarget);
    };
    const handleFixedLeft = (colItem) => {
      if (modalItem?.label) {
        emit("fixedLeft", colItem);
      }
    };
    const handleFixedRight = (colItem) => {
      if (modalItem?.label) {
        emit("fixedRight", colItem);
      }
    };
    const handleChildSortChange = (colItems, parent) => {
      if (modalItem?.label) {
        emit("sortChange", colItems, parent);
      }
    };
    const handleCheckedChange = (colItem, checked) => {
      if (modalItem?.label) {
        emit("checkedChange", colItem, checked);
      }
    };
    const handleColWidthChange = (item, width) => {
      emit("colWidthChange", item, width);
    };
    const handleSortChange = (colItems) => {
      handleChildSortChange(colItems, props.parent);
    };
    return (_ctx, _cache) => {
      const _component_ToolColumnList = vue.resolveComponent("ToolColumnList", true);
      return vue.openBlock(), vue.createBlock(vue.unref(VueDraggable), {
        itemKey: "uid",
        animation: 300,
        modelValue: __props.data,
        setData: () => void 0,
        handle: ".ele-tool-column-handle",
        componentData: { class: "ele-tool-column-list" },
        forceFallback: true,
        "onUpdate:modelValue": handleSortChange
      }, {
        item: vue.withCtx(({ element: d }) => [
          vue.createElementVNode("div", _hoisted_1, [
            vue.createElementVNode("div", _hoisted_2, [
              __props.sortable ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_3, [
                vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.HolderOutlined))
                  ]),
                  _: 1
                })
              ])) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", _hoisted_4, [
                vue.createVNode(vue.unref(elementPlus.ElCheckbox), {
                  label: d.label,
                  modelValue: d.checked,
                  "onUpdate:modelValue": (v) => handleCheckedChange(d, v)
                }, null, 8, ["label", "modelValue", "onUpdate:modelValue"])
              ]),
              __props.allowFixed ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_5, [
                vue.createElementVNode("div", {
                  class: vue.normalizeClass(["ele-tool-column-fixed-item", { "is-active": d.fixed === true || d.fixed === "left" }]),
                  onClick: ($event) => handleFixedLeft(d),
                  onMouseover: handleFixedLeftTooltip
                }, [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.VerticalRightOutlined))
                    ]),
                    _: 1
                  })
                ], 42, _hoisted_6),
                vue.createElementVNode("div", {
                  class: vue.normalizeClass(["ele-tool-column-fixed-item", { "is-active": d.fixed === "right" }]),
                  onClick: ($event) => handleFixedRight(d),
                  onMouseover: handleFixedRightTooltip
                }, [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.VerticalLeftOutlined))
                    ]),
                    _: 1
                  })
                ], 42, _hoisted_7)
              ])) : vue.createCommentVNode("", true),
              __props.allowWidth ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_8, [
                vue.createVNode(vue.unref(elementPlus.ElInput), {
                  size: "small",
                  maxlength: 12,
                  modelValue: d.width,
                  placeholder: __props.columnWidthPlaceholder,
                  "onUpdate:modelValue": (v) => handleColWidthChange(d, v)
                }, null, 8, ["modelValue", "placeholder", "onUpdate:modelValue"])
              ])) : vue.createCommentVNode("", true)
            ]),
            d.children && d.children.length ? (vue.openBlock(), vue.createBlock(_component_ToolColumnList, {
              key: 0,
              data: d.children,
              parent: d,
              sortable: __props.sortable,
              allowWidth: __props.allowWidth,
              columnWidthPlaceholder: __props.columnWidthPlaceholder,
              onSortChange: handleChildSortChange,
              onCheckedChange: handleCheckedChange,
              onFixedLeft: handleFixedLeft,
              onFixedRight: handleFixedRight,
              onFixedLeftTooltip: handleChildFixedLeftTooltip,
              onFixedRightTooltip: handleChildFixedRightTooltip,
              onColWidthChange: handleColWidthChange
            }, null, 8, ["data", "parent", "sortable", "allowWidth", "columnWidthPlaceholder"])) : vue.createCommentVNode("", true)
          ])
        ]),
        _: 1
      }, 8, ["modelValue"]);
    };
  }
});
module.exports = _sfc_main;
