import { defineComponent, createElementBlock, openBlock, normalizeStyle, normalizeClass, renderSlot, Fragment, renderList, createBlock, unref } from "vue";
import { useLocale } from "../ele-config-provider/receiver";
import ItemRender from "./components/item-render";
import { buttonsEmits, buttonsProps } from "./props";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "EleButtons" },
  __name: "index",
  props: buttonsProps,
  emits: buttonsEmits,
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { lang } = useLocale("buttons", props);
    const handleItemClick = (command, e) => {
      emit("itemClick", command, e);
    };
    return (_ctx, _cache) => {
      return _ctx.gap != null || _ctx.wrap != null || _ctx.modalFooter ? (openBlock(), createElementBlock("div", {
        key: 0,
        class: normalizeClass(["ele-buttons-wrap ele-buttons", {
          "is-nowrap": _ctx.wrap === false,
          "is-gap": _ctx.gap != null,
          "is-modal-footer": _ctx.modalFooter
        }]),
        style: normalizeStyle(_ctx.gap == null || _ctx.gap === true ? {} : { gap: `${_ctx.gap || 0}px` })
      }, [
        (openBlock(true), createElementBlock(Fragment, null, renderList(_ctx.items, (item, index) => {
          return openBlock(), createBlock(ItemRender, {
            key: item.key ?? item.command ?? item.title,
            item,
            divider: index === 0 ? false : _ctx.divider,
            type: _ctx.type,
            wrapClass: false,
            lang: unref(lang),
            onItemClick: handleItemClick
          }, null, 8, ["item", "divider", "type", "lang"]);
        }), 128)),
        renderSlot(_ctx.$slots, "default")
      ], 6)) : (openBlock(), createElementBlock(Fragment, { key: 1 }, [
        (openBlock(true), createElementBlock(Fragment, null, renderList(_ctx.items, (item, index) => {
          return openBlock(), createBlock(ItemRender, {
            key: item.key ?? item.command ?? item.title,
            item,
            divider: index === 0 ? false : _ctx.divider,
            type: _ctx.type,
            wrapClass: true,
            lang: unref(lang),
            onItemClick: handleItemClick
          }, null, 8, ["item", "divider", "type", "lang"]);
        }), 128)),
        renderSlot(_ctx.$slots, "default")
      ], 64));
    };
  }
});
export {
  _sfc_main as default
};
