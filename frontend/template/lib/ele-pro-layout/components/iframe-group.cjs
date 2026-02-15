"use strict";
const vue = require("vue");
const hook = require("../../utils/hook");
const util = require("../util");
const _hoisted_1 = { class: "ele-admin-iframe-wrap" };
const _hoisted_2 = ["data-id", "src"];
const _hoisted_3 = ["data-id", "src"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "IframeGroup" },
  __name: "iframe-group",
  props: {
    /** 是否支持内嵌缓存 */
    keepAlive: Boolean,
    /** 内嵌切换动画 */
    transitionName: String,
    /** 内嵌进入动画延迟时间 */
    transitionDelay: Number,
    /** 页签数据 */
    tabData: {
      type: Array,
      required: true
    },
    /** 页签选中 */
    tabActive: String
  },
  setup(__props) {
    const props = __props;
    const [startActiveTimer, stopActiveTimer] = hook.useTimer();
    const data = vue.computed(() => {
      const list = [];
      props.tabData.forEach((t) => {
        const isAlive = t.meta?.keepAlive !== false;
        if (t.key && t.meta?.iframe && isAlive) {
          const src = util.getIframeSrc(t.fullPath, t.meta.iframe);
          list.push({ id: t.key, src, refresh: t.refresh });
        }
      });
      return list.sort((a, b) => a.id === b.id ? 0 : a.id > b.id ? 1 : -1);
    });
    const dataActive = vue.computed(() => {
      if (!props.tabActive || !data.value.length || !data.value.some((d) => d.id === props.tabActive)) {
        return;
      }
      return props.tabActive;
    });
    const active = vue.ref(dataActive.value);
    const handleLeave = (delay) => {
      if (!dataActive.value) {
        active.value = null;
        return;
      }
      if (!delay) {
        active.value = dataActive.value;
        return;
      }
      startActiveTimer(() => {
        vue.nextTick(() => {
          active.value = dataActive.value;
        });
      }, delay);
    };
    vue.watch(dataActive, () => {
      stopActiveTimer();
      if (active.value == null) {
        handleLeave(props.transitionName ? props.transitionDelay : void 0);
      } else if (!props.transitionName) {
        handleLeave();
      } else {
        active.value = null;
      }
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        !__props.transitionName ? (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 0 }, vue.renderList(data.value, (item) => {
          return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
            key: item.id
          }, [
            !item.refresh ? vue.withDirectives((vue.openBlock(), vue.createElementBlock("iframe", {
              key: 0,
              "data-id": item.id,
              src: item.src,
              class: "ele-admin-iframe"
            }, null, 8, _hoisted_2)), [
              [vue.vShow, active.value === item.id]
            ]) : vue.createCommentVNode("", true)
          ], 64);
        }), 128)) : (vue.openBlock(), vue.createBlock(vue.TransitionGroup, {
          key: 1,
          appear: true,
          name: __props.transitionName,
          onAfterLeave: _cache[0] || (_cache[0] = ($event) => handleLeave())
        }, {
          default: vue.withCtx(() => [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(data.value, (item) => {
              return vue.openBlock(), vue.createElementBlock(vue.Fragment, {
                key: item.id
              }, [
                !item.refresh ? vue.withDirectives((vue.openBlock(), vue.createElementBlock("iframe", {
                  key: 0,
                  "data-id": item.id,
                  src: item.src,
                  class: "ele-admin-iframe"
                }, null, 8, _hoisted_3)), [
                  [vue.vShow, active.value === item.id]
                ]) : vue.createCommentVNode("", true)
              ], 64);
            }), 128))
          ]),
          _: 1
        }, 8, ["name"]))
      ]);
    };
  }
});
module.exports = _sfc_main;
