"use strict";
const vue = require("vue");
const JsBarCode = require("jsbarcode");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleBarCode" },
  __name: "index",
  props: props.barCodeProps,
  setup(__props, { expose: __expose }) {
    const props2 = __props;
    const rootRef = vue.ref(null);
    let instance = null;
    const render = () => {
      if (!props2.value || !rootRef.value) {
        return;
      }
      try {
        instance = new JsBarCode(rootRef.value, props2.value, props2.options);
      } catch (e) {
        console.error(e);
      }
    };
    const getInstance = () => {
      return instance;
    };
    vue.watch(
      () => props2.value,
      () => {
        render();
      }
    );
    vue.watch(
      () => props2.options,
      () => {
        render();
      },
      { deep: true }
    );
    vue.watch(
      () => props2.tag,
      () => {
        vue.nextTick(() => {
          render();
        });
      }
    );
    vue.onMounted(() => {
      render();
    });
    vue.onBeforeUnmount(() => {
      instance = null;
    });
    __expose({
      instance,
      getInstance
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.tag), {
        ref_key: "rootRef",
        ref: rootRef,
        style: vue.normalizeStyle(_ctx.value ? void 0 : { display: "none" })
      }, null, 8, ["style"]);
    };
  }
});
module.exports = _sfc_main;
