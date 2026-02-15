"use strict";
const vue = require("vue");
const MainContent = require("../../ele-loading/components/main-content");
const FileGridItem = require("./file-grid-item");
const _hoisted_1 = {
  key: 0,
  class: "ele-file-list-header"
};
const _hoisted_2 = { class: "ele-file-list-body" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "FileGrid" },
  __name: "file-grid",
  props: {
    /** 文件数据 */
    data: Array,
    /** 后缀对应的图标 */
    icons: Array,
    /** 选择框类型 */
    selectionType: String,
    /** 已选中的数据 */
    selections: Array,
    /** 单选选中数据 */
    current: Object,
    /** 是否是全选 */
    isCheckAll: Boolean,
    /** 是否是半选 */
    isIndeterminate: Boolean,
    /** 全选按钮文字 */
    checkAllText: String,
    /** 选中后的文字 */
    selectedText: String,
    /** 文件右键菜单是否打开 */
    ctxMenuDropdownVisible: Boolean,
    /** 当前打开的右键菜单对应的文件数据 */
    contextMenuFileItem: Object
  },
  emits: {
    checkAllChange: () => true,
    itemClick: (_item) => true,
    itemCheckChange: (_item) => true,
    itemContextOpen: (_option) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const headerText = vue.computed(() => {
      if (!props.selections || !props.selections.length) {
        return props.checkAllText;
      }
      if (!props.selectedText) {
        return "";
      }
      return props.selectedText.replace(
        /\{\s*total\s*\}/g,
        String(props.selections.length)
      );
    });
    const handleCheckAllChange = () => {
      emit("checkAllChange");
    };
    const handleItemClick = (item) => {
      emit("itemClick", item);
    };
    const handleItemCheckChange = (item) => {
      emit("itemCheckChange", item);
    };
    const handleItemContextOpen = (option) => {
      emit("itemContextOpen", option);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(MainContent, { class: "ele-file-list" }, {
        default: vue.withCtx(() => [
          __props.selectionType === "checkbox" ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
            vue.createElementVNode("div", {
              class: "ele-file-list-selection",
              onClick: vue.withModifiers(handleCheckAllChange, ["stop"])
            }, [
              vue.createElementVNode("i", {
                class: vue.normalizeClass(["ele-file-list-checkbox", [
                  { "is-checked": __props.isCheckAll },
                  { "is-indeterminate": __props.isIndeterminate }
                ]])
              }, null, 2),
              vue.createElementVNode("div", null, vue.toDisplayString(headerText.value), 1)
            ])
          ])) : vue.createCommentVNode("", true),
          vue.createElementVNode("div", _hoisted_2, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(__props.data, (item) => {
              return vue.openBlock(), vue.createBlock(FileGridItem, {
                key: item.key,
                item,
                selectionType: __props.selectionType,
                selections: __props.selections,
                current: __props.current,
                icons: __props.icons,
                ctxMenuDropdownVisible: __props.ctxMenuDropdownVisible && __props.contextMenuFileItem === item,
                onClick: handleItemClick,
                onCheckChange: handleItemCheckChange,
                onContextOpen: handleItemContextOpen
              }, vue.createSlots({ _: 2 }, [
                vue.renderList(Object.keys(_ctx.$slots), (name) => {
                  return {
                    name,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, name, vue.mergeProps({ ref_for: true }, slotProps || {}))
                    ])
                  };
                })
              ]), 1032, ["item", "selectionType", "selections", "current", "icons", "ctxMenuDropdownVisible"]);
            }), 128))
          ])
        ]),
        _: 3
      });
    };
  }
});
module.exports = _sfc_main;
