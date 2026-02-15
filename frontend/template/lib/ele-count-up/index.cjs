"use strict";
const vue = require("vue");
const countup_js = require("countup.js");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCountUp" },
  __name: "index",
  props: props.countUpProps,
  emits: props.countUpEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const isFunction = (value) => typeof value === "function";
    let instance;
    const rootRef = vue.ref(null);
    const create = () => {
      const elem = vue.unref(rootRef);
      if (instance || !elem) {
        return;
      }
      const ins = new countup_js.CountUp(elem, props2.endVal ?? 0, props2.options);
      if (ins.error) {
        console.warn(ins);
        return;
      }
      instance = ins;
    };
    const printValue = (value) => {
      if (instance && isFunction(instance.printValue)) {
        return instance.printValue(value);
      }
    };
    const start = (callback) => {
      if (instance && isFunction(instance.start)) {
        return instance.start(callback);
      }
    };
    const pauseResume = () => {
      if (instance && isFunction(instance.pauseResume)) {
        return instance.pauseResume();
      }
    };
    const reset = () => {
      if (instance && isFunction(instance.reset)) {
        return instance.reset();
      }
    };
    const update = (newEndVal) => {
      if (instance && isFunction(instance.update)) {
        return instance.update(newEndVal ?? 0);
      }
    };
    const destroy = () => {
      reset();
      instance = null;
    };
    vue.watch(
      () => props2.endVal,
      (value) => {
        update(value);
      }
    );
    vue.watch(
      () => props2.options,
      () => {
        destroy();
        create();
        emit("ready", instance);
      }
    );
    vue.onMounted(() => {
      create();
      if (props2.delay < 0) {
        emit("ready", instance);
        return;
      }
      setTimeout(() => {
        if (instance && isFunction(instance.start)) {
          instance.start(() => {
            emit("ready", instance);
          });
        }
      }, props2.delay);
    });
    vue.onBeforeUnmount(() => {
      destroy();
    });
    __expose({
      printValue,
      start,
      pauseResume,
      reset,
      update
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("span", {
        ref_key: "rootRef",
        ref: rootRef
      }, null, 512);
    };
  }
});
module.exports = _sfc_main;
