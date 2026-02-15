"use strict";
const vue = require("vue");
const props$1 = require("../ele-tabs/props");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTabWrap" },
  __name: "index",
  props: props.tabWrapProps,
  setup(__props) {
    const props2 = __props;
    const tabMethods = {};
    const data = vue.reactive({
      size: props2.size,
      type: props2.type,
      setTabMethods: (methods) => {
        tabMethods.triggerTabItemClick = methods.triggerTabItemClick;
        tabMethods.triggerItemContextMenu = methods.triggerItemContextMenu;
      },
      triggerTabItemClick: (item, tabName, e) => {
        if (tabMethods.triggerTabItemClick) {
          tabMethods.triggerTabItemClick(item, tabName, e);
        }
      },
      triggerItemContextMenu: (item, tabName, e) => {
        if (tabMethods.triggerItemContextMenu) {
          tabMethods.triggerItemContextMenu(item, tabName, e);
        }
      }
    });
    vue.provide(props$1.TAB_WRAP_KEY, data);
    vue.watch(
      () => props2.size,
      () => {
        data.size = props2.size;
      }
    );
    vue.watch(
      () => props2.type,
      () => {
        data.type = props2.type;
      }
    );
    vue.onBeforeUnmount(() => {
      tabMethods.triggerTabItemClick = void 0;
      tabMethods.triggerItemContextMenu = void 0;
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-tab-wrap ele-tabs-wrap", [
          { "is-small": _ctx.size === "small" },
          { "is-large": _ctx.size === "large" },
          { "is-simple": _ctx.type === "simple" },
          { "is-indicator": _ctx.type === "indicator" },
          { "is-button": _ctx.type === "button" },
          { "is-tag": _ctx.type === "tag" }
        ]])
      }, [
        vue.renderSlot(_ctx.$slots, "default")
      ], 2);
    };
  }
});
module.exports = _sfc_main;
