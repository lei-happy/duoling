"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const hook = require("../../utils/hook");
const EleDropdown = require("../../ele-dropdown/index");
const EleTabTool = require("../../ele-tab-tool/index");
const _hoisted_1 = { style: { textAlign: "center", outline: "none" } };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "TabDropdown" },
  __name: "tab-dropdown",
  props: {
    /** 右键菜单 */
    items: Array,
    /** 右键菜单属性 */
    dropdownProps: Object,
    /** 是否点击后自动关闭菜单 */
    autoClose: {
      type: Boolean,
      default: true
    }
  },
  emits: {
    menuClick: (_command) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const [startAutoCloseTimer] = hook.useTimer(150);
    const dropdownRef = vue.ref(null);
    const handleCommand = (command) => {
      emit("menuClick", command);
      if (props.autoClose) {
        startAutoCloseTimer(() => {
          if (dropdownRef.value) {
            dropdownRef.value.handleClose();
          }
        });
      }
    };
    __expose({
      dropdownRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleTabTool, null, {
        default: vue.withCtx(() => [
          vue.createVNode(EleDropdown, vue.mergeProps({
            placement: "bottom-end",
            popperClass: "ele-tab-popup",
            popperOptions: {
              modifiers: [{ name: "offset", options: { offset: [12, 8] } }]
            },
            validateEvent: false
          }, __props.dropdownProps || {}, {
            ref_key: "dropdownRef",
            ref: dropdownRef,
            items: __props.items,
            componentType: "pro",
            onCommand: handleCommand
          }), {
            default: vue.withCtx(() => [
              vue.createElementVNode("div", _hoisted_1, [
                vue.renderSlot(_ctx.$slots, "icon", {}, () => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), {
                    class: "ele-tab-icon",
                    style: { verticalAlign: "-3px" }
                  }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.ArrowDown))
                    ]),
                    _: 1
                  })
                ])
              ])
            ]),
            _: 3
          }, 16, ["items"])
        ]),
        _: 3
      });
    };
  }
});
module.exports = _sfc_main;
