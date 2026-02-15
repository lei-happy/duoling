"use strict";
const vue = require("vue");
const receiver = require("../ele-config-provider/receiver");
const ItemRender = require("./components/item-render");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleButtons" },
  __name: "index",
  props: props.buttonsProps,
  emits: props.buttonsEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("buttons", props2);
    const handleItemClick = (command, e) => {
      emit("itemClick", command, e);
    };
    return (_ctx, _cache) => {
      return _ctx.gap != null || _ctx.wrap != null || _ctx.modalFooter ? (vue.openBlock(), vue.createElementBlock("div", {
        key: 0,
        class: vue.normalizeClass(["ele-buttons-wrap ele-buttons", {
          "is-nowrap": _ctx.wrap === false,
          "is-gap": _ctx.gap != null,
          "is-modal-footer": _ctx.modalFooter
        }]),
        style: vue.normalizeStyle(_ctx.gap == null || _ctx.gap === true ? {} : { gap: `${_ctx.gap || 0}px` })
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.items, (item, index) => {
          return vue.openBlock(), vue.createBlock(ItemRender, {
            key: item.key ?? item.command ?? item.title,
            item,
            divider: index === 0 ? false : _ctx.divider,
            type: _ctx.type,
            wrapClass: false,
            lang: vue.unref(lang),
            onItemClick: handleItemClick
          }, null, 8, ["item", "divider", "type", "lang"]);
        }), 128)),
        vue.renderSlot(_ctx.$slots, "default")
      ], 6)) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.items, (item, index) => {
          return vue.openBlock(), vue.createBlock(ItemRender, {
            key: item.key ?? item.command ?? item.title,
            item,
            divider: index === 0 ? false : _ctx.divider,
            type: _ctx.type,
            wrapClass: true,
            lang: vue.unref(lang),
            onItemClick: handleItemClick
          }, null, 8, ["item", "divider", "type", "lang"]);
        }), 128)),
        vue.renderSlot(_ctx.$slots, "default")
      ], 64));
    };
  }
});
module.exports = _sfc_main;
