"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../../utils/common");
const _hoisted_1 = {
  key: 0,
  class: "ele-menu-title"
};
const _hoisted_2 = ["href", "target"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ItemTitle" },
  __name: "item-title",
  props: {
    /** 菜单项数据 */
    item: {
      type: Object,
      required: true
    },
    /** 是否需要标题 */
    showTitle: {
      type: Boolean,
      default: true
    },
    /** 是否需要链接 */
    showLink: Boolean
  },
  emits: {
    itemClick: (_item, _e) => true,
    itemMouseenter: (_item, _e) => true,
    itemMouseleave: (_item, _e) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const handleItemClick = (item, e) => {
      if (props.showLink && (common.isExternalLink(item.path) || item.path && item.pathTarget === "_blank")) {
        e.stopPropagation();
      }
      emit("itemClick", item, e);
    };
    const handleItemMouseenter = (item, e) => {
      emit("itemMouseenter", item, e);
    };
    const handleItemMouseleave = (item, e) => {
      emit("itemMouseleave", item, e);
    };
    return (_ctx, _cache) => {
      const _component_RouterLink = vue.resolveComponent("RouterLink");
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.renderSlot(_ctx.$slots, "icon", {
          item: __props.item,
          icon: __props.item.icon
        }, () => [
          __props.item.icon ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.normalizeProps(vue.mergeProps({ key: 0 }, __props.item.iconProps || {})), {
            default: vue.withCtx(() => [
              (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(__props.item.icon), {
                style: vue.normalizeStyle(__props.item.iconStyle)
              }, null, 8, ["style"]))
            ]),
            _: 1
          }, 16)) : vue.createCommentVNode("", true)
        ]),
        __props.showTitle ? vue.renderSlot(_ctx.$slots, "title", {
          key: 0,
          item: __props.item,
          title: __props.item.title
        }, () => [
          __props.item.title ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_1, vue.toDisplayString(__props.item.title), 1)) : vue.createCommentVNode("", true)
        ]) : vue.createCommentVNode("", true),
        __props.item.badge != null ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElBadge), vue.normalizeProps(vue.mergeProps({ key: 1 }, __props.item.badge)), null, 16)) : vue.createCommentVNode("", true),
        vue.createElementVNode("div", {
          class: "ele-menu-trigger",
          onClick: _cache[0] || (_cache[0] = (e) => handleItemClick(__props.item, e)),
          onMouseenter: _cache[1] || (_cache[1] = (e) => handleItemMouseenter(__props.item, e)),
          onMouseleave: _cache[2] || (_cache[2] = (e) => handleItemMouseleave(__props.item, e))
        }, [
          __props.showLink ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
            vue.unref(common.isExternalLink)(__props.item.path) ? (vue.openBlock(), vue.createElementBlock("a", {
              key: 0,
              href: __props.item.path,
              target: __props.item.pathTarget || "_blank",
              class: "ele-menu-link"
            }, null, 8, _hoisted_2)) : __props.item.path ? (vue.openBlock(), vue.createBlock(_component_RouterLink, {
              key: 1,
              to: __props.item.path,
              target: __props.item.pathTarget,
              class: "ele-menu-link"
            }, null, 8, ["to", "target"])) : vue.createCommentVNode("", true)
          ], 64)) : vue.createCommentVNode("", true)
        ], 32)
      ], 64);
    };
  }
});
module.exports = _sfc_main;
