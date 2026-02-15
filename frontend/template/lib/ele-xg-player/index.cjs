"use strict";
const vue = require("vue");
const Player = require("xgplayer");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleXgPlayer" },
  __name: "index",
  props: {
    config: {
      type: Object,
      required: true
    }
  },
  emits: {
    player: (_player) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    let player = null;
    const rootRef = vue.ref(null);
    const init = () => {
      destroy();
      if (rootRef.value && props.config?.url) {
        player = new Player(
          Object.assign({}, props.config, { el: rootRef.value })
        );
        emit("player", player);
      }
    };
    const destroy = () => {
      if (player && typeof player.destroy === "function") {
        player.destroy();
        player = null;
      }
    };
    vue.onMounted(() => {
      init();
    });
    vue.onBeforeUnmount(() => {
      destroy();
    });
    vue.watch(
      () => props.config,
      () => {
        init();
      }
    );
    __expose({
      player
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "rootRef",
        ref: rootRef
      }, null, 512);
    };
  }
});
module.exports = _sfc_main;
