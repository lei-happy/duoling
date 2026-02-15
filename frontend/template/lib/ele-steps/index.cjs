"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleSteps" },
  __name: "index",
  props: props.stepsProps,
  setup(__props, { expose: __expose }) {
    const props2 = __props;
    const { optionData, reloadOptions } = hook.useProOptions(props2, "items");
    const stepsRef = vue.ref(null);
    __expose({
      reloadOptions,
      stepsRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElSteps), vue.mergeProps(vue.unref(common.omit)(_ctx.$props, ["items", "type"]), {
        ref_key: "stepsRef",
        ref: stepsRef,
        class: ["ele-steps", { "is-inline": _ctx.direction === "horizontal" && _ctx.type === "inline" }]
      }), {
        default: vue.withCtx(() => [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(optionData), (item, index) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElStep), vue.mergeProps({ key: index }, { ref_for: true }, item), vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots).filter((k) => "default" !== k), (name) => {
                return {
                  name,
                  fn: vue.withCtx(() => [
                    vue.renderSlot(_ctx.$slots, name, {
                      index,
                      item
                    })
                  ])
                };
              })
            ]), 1040);
          }), 128))
        ]),
        _: 3
      }, 16, ["class"]);
    };
  }
});
module.exports = _sfc_main;
