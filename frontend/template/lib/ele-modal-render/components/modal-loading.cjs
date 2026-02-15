"use strict";
const vue = require("vue");
const LoadingSpinner = require("../../ele-loading/components/loading-spinner");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ModalLoading", inheritAttrs: false },
  __name: "modal-loading",
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Teleport, { to: "body" }, [
        vue.createVNode(LoadingSpinner, {
          plain: true,
          loading: true,
          class: "ele-modal-render-loading"
        })
      ]);
    };
  }
});
module.exports = _sfc_main;
