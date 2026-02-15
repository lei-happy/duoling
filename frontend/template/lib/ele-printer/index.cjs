"use strict";
const vue = require("vue");
const util = require("./util");
const props = require("./props");
const _hoisted_1 = { key: 0 };
const _hoisted_2 = { key: 1 };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ElePrinter", inheritAttrs: false },
  __name: "index",
  props: props.printerProps,
  emits: props.printerEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const doPrint = util.usePrinter(() => {
      visible.value = false;
      updateModelValue(false);
      handleDone();
    });
    const container = vue.shallowRef(util.getPrintContainer());
    const visible = vue.ref(false);
    const isStatic = vue.computed(() => props2.static);
    const print = (options) => {
      if (visible.value) {
        return;
      }
      visible.value = true;
      vue.nextTick(() => {
        const option = {
          title: props2.title,
          margin: props2.margin,
          direction: props2.direction,
          orientation: props2.orientation,
          options: util.mergeOptions(props2.options, options)
        };
        doPrint(option, props2.target);
      });
    };
    const handleDone = () => {
      emit("done");
    };
    const updateModelValue = (value) => {
      emit("update:modelValue", value);
    };
    vue.watch(
      () => props2.modelValue,
      (modelValue) => {
        if (modelValue) {
          print();
        }
      }
    );
    vue.onMounted(() => {
      if (props2.modelValue) {
        print();
      }
    });
    __expose({
      print
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Teleport, {
        to: container.value,
        disabled: isStatic.value && !visible.value
      }, [
        vue.createElementVNode("table", vue.mergeProps(_ctx.$attrs, {
          class: ["ele-printer", [{ "is-open": visible.value }, { "is-static": isStatic.value }]]
        }), [
          _ctx.$slots.header ? (vue.openBlock(), vue.createElementBlock("thead", _hoisted_1, [
            vue.createElementVNode("tr", null, [
              vue.createElementVNode("td", null, [
                vue.createElementVNode("div", {
                  class: "ele-printer-header",
                  style: vue.normalizeStyle(_ctx.headerStyle)
                }, [
                  vue.renderSlot(_ctx.$slots, "header")
                ], 4)
              ])
            ])
          ])) : vue.createCommentVNode("", true),
          vue.createElementVNode("tbody", null, [
            vue.createElementVNode("tr", null, [
              vue.createElementVNode("td", null, [
                vue.createElementVNode("div", {
                  class: "ele-printer-body",
                  style: vue.normalizeStyle(_ctx.bodyStyle)
                }, [
                  vue.renderSlot(_ctx.$slots, "default")
                ], 4)
              ])
            ])
          ]),
          _ctx.$slots.footer ? (vue.openBlock(), vue.createElementBlock("tfoot", _hoisted_2, [
            vue.createElementVNode("tr", null, [
              vue.createElementVNode("td", null, [
                vue.createElementVNode("div", {
                  class: "ele-printer-footer",
                  style: vue.normalizeStyle(_ctx.footerStyle)
                }, [
                  vue.renderSlot(_ctx.$slots, "footer")
                ], 4)
              ])
            ])
          ])) : vue.createCommentVNode("", true)
        ], 16)
      ], 8, ["to", "disabled"]);
    };
  }
});
module.exports = _sfc_main;
