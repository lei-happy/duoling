"use strict";
const vue = require("vue");
const _hoisted_1 = { class: "ele-pro-form-builder-code-line-numbers" };
const _hoisted_2 = { class: "ele-pro-form-builder-code-pre" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "CodeViewer" },
  __name: "code-viewer",
  props: {
    code: {}
  },
  setup(__props) {
    const props = __props;
    const codeLines = vue.ref(1);
    vue.watch(
      () => props.code,
      (code) => {
        codeLines.value = code ? code.split("\n").length : 1;
      },
      { immediate: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock(vue.Fragment, null, [
        vue.createElementVNode("div", _hoisted_1, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(codeLines.value, (n) => {
            return vue.openBlock(), vue.createElementBlock("div", { key: n }, vue.toDisplayString(n), 1);
          }), 128))
        ]),
        vue.createElementVNode("pre", _hoisted_2, vue.toDisplayString(__props.code), 1)
      ], 64);
    };
  }
});
module.exports = _sfc_main;
