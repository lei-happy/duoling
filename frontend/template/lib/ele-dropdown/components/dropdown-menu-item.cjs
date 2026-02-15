"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const _hoisted_1 = {
  key: 0,
  class: "ele-dropdown-menu-divider"
};
const _hoisted_2 = { key: 1 };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "DropdownMenuItem" },
  __name: "dropdown-menu-item",
  props: {
    /** 菜单项数据 */
    item: {
      type: Object,
      required: true
    },
    /** 选中的菜单 */
    selected: [String, Number, Object],
    /** 自定义图标属性 */
    iconProps: Object
  },
  emits: {
    itemClick: (_item, _e) => true,
    wrapperContext: (_e) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const itemRef = vue.ref(null);
    const subMenuRef = vue.ref(null);
    const placement = vue.ref();
    const handleItemClick = (e) => {
      if (props.item.disabled) {
        return;
      }
      emit("itemClick", props.item, e);
    };
    const handleItemMouseenter = () => {
      const subMenuEl = subMenuRef.value;
      if (!subMenuEl || !itemRef.value) {
        return;
      }
      const rect = itemRef.value.getBoundingClientRect();
      const rightOver = rect.right + subMenuEl.offsetWidth > window.innerWidth;
      const bottomOver = rect.top + subMenuEl.offsetHeight > window.innerHeight;
      if (rightOver && bottomOver) {
        placement.value = "leftEnd";
      } else if (rightOver) {
        placement.value = "leftStart";
      } else if (bottomOver) {
        placement.value = "rightEnd";
      } else {
        placement.value = void 0;
      }
    };
    const handleWrapperContext = (e) => {
      emit("wrapperContext", e);
    };
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        __props.item.divided ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_1)) : vue.createCommentVNode("", true),
        vue.createElementVNode("div", {
          ref_key: "itemRef",
          ref: itemRef,
          class: vue.normalizeClass(["ele-dropdown-menu-item", [
            { "is-disabled": !!__props.item.disabled },
            { "is-active": __props.item.command != null && __props.selected === __props.item.command },
            { "is-danger": !!__props.item.danger }
          ]]),
          onClick: vue.withModifiers(handleItemClick, ["stop"]),
          onMouseenter: handleItemMouseenter
        }, [
          __props.item.slot && __props.item.slot !== "default" && __props.item.slot !== "subMenus" && _ctx.$slots[__props.item.slot] ? vue.renderSlot(_ctx.$slots, __props.item.slot, {
            key: 0,
            item: __props.item
          }) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
            __props.item.icon ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.mergeProps({ key: 0 }, { ...__props.iconProps || {}, ...__props.item.iconProps || {} })), {
              default: vue.withCtx(() => [
                (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.item.icon), {
                  style: vue.normalizeStyle(__props.item.iconStyle)
                }, null, 8, ["style"]))
              ]),
              _: 1
            }, 16)) : vue.createCommentVNode("", true),
            __props.item.title ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_2, vue.toDisplayString(__props.item.title), 1)) : vue.createCommentVNode("", true)
          ], 64)),
          __props.item.children && __props.item.children.length ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 2 }, [
            vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-dropdown-menu-item-arrow" }, {
              default: vue.withCtx(() => [
                vue.createVNode(vue.unref(index.ArrowRight))
              ]),
              _: 1
            }),
            vue.createElementVNode("div", {
              ref_key: "subMenuRef",
              ref: subMenuRef,
              class: vue.normalizeClass(["ele-dropdown-wrapper is-sub-menu", [
                { "is-right-end": placement.value === "rightEnd" },
                { "is-left-start": placement.value === "leftStart" },
                { "is-left-end": placement.value === "leftEnd" }
              ]]),
              onContextmenu: handleWrapperContext,
              onClick: _cache[0] || (_cache[0] = vue.withModifiers(() => {
              }, ["stop"]))
            }, [
              vue.renderSlot(_ctx.$slots, "subMenus")
            ], 34)
          ], 64)) : vue.createCommentVNode("", true)
        ], 34)
      ], 64);
    };
  }
});
module.exports = _sfc_main;
