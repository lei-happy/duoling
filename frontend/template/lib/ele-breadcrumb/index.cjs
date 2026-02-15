"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const props = require("./props");
const _hoisted_1 = { key: 1 };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleBreadcrumb" },
  __name: "index",
  props: props.breadcrumbProps,
  setup(__props, { expose: __expose }) {
    const props2 = __props;
    const breadcrumbRef = vue.ref(null);
    const breadcrumbSeparator = vue.computed(() => {
      if (typeof props2.separator !== "string") {
        return;
      }
      return props2.separator;
    });
    const breadcrumbSeparatorIcon = vue.computed(
      () => {
        if (props2.separatorIcon != null && props2.separatorIcon !== "") {
          return props2.separatorIcon;
        }
        if (props2.separator != null && typeof props2.separator !== "string") {
          return props2.separator;
        }
        return props2.separatorIcon;
      }
    );
    __expose({
      breadcrumbRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElBreadcrumb), {
        ref_key: "breadcrumbRef",
        ref: breadcrumbRef,
        separator: breadcrumbSeparator.value,
        separatorIcon: breadcrumbSeparatorIcon.value,
        class: "ele-breadcrumb"
      }, {
        default: vue.withCtx(() => [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.items, (item) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElBreadcrumbItem), {
              key: item.key ?? item.title,
              replace: item.replace,
              to: item.to
            }, {
              default: vue.withCtx(() => [
                item.slot && item.slot !== "default" && _ctx.$slots[item.slot] ? vue.renderSlot(_ctx.$slots, item.slot, {
                  key: 0,
                  item
                }) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                  item.icon ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), vue.mergeProps({
                    key: 0,
                    ref_for: true
                  }, item.iconProps || {}), {
                    default: vue.withCtx(() => [
                      (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(item.icon), {
                        style: vue.normalizeStyle(item.iconStyle)
                      }, null, 8, ["style"]))
                    ]),
                    _: 2
                  }, 1040)) : vue.createCommentVNode("", true),
                  item.title ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_1, vue.toDisplayString(item.title), 1)) : vue.createCommentVNode("", true)
                ], 64))
              ]),
              _: 2
            }, 1032, ["replace", "to"]);
          }), 128))
        ]),
        _: 3
      }, 8, ["separator", "separatorIcon"]);
    };
  }
});
module.exports = _sfc_main;
