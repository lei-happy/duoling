"use strict";
const vue = require("vue");
const common = require("../utils/common");
const receiver = require("../ele-config-provider/receiver");
const util = require("../ele-pro-layout/util");
const EleModal = require("../ele-modal/index");
const MapView = require("./components/map-view");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleMapPicker" },
  __name: "index",
  props: props.mapPickerProps,
  emits: props.mapPickerEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const { lang, globalConfig } = receiver.useLocale("map", props$1);
    const isResponsive = util.useResponsive(props$1);
    const mapRef = vue.ref(null);
    const aMapKey = vue.computed(() => props$1.mapKey || globalConfig.mapKey);
    const mapProps = vue.computed(() => {
      return common.pick(props$1, props.mapPropKeys);
    });
    const updateModelValue = (visible) => {
      emit("update:modelValue", visible);
    };
    const handleMapDone = (ins) => {
      emit("mapDone", ins);
    };
    const handleDone = (result) => {
      emit("done", result);
    };
    vue.watch(
      () => props$1.modelValue,
      (visible) => {
        if (visible) {
          mapRef.value && mapRef.value.showInitSelected();
        }
      }
    );
    __expose({
      mapRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, vue.mergeProps({
        width: "740px",
        title: vue.unref(lang).title
      }, _ctx.modalProps || {}, {
        modelValue: _ctx.modelValue,
        class: ["ele-map-picker", { "is-responsive": vue.unref(isResponsive) }],
        "onUpdate:modelValue": updateModelValue
      }), vue.createSlots({
        default: vue.withCtx(() => [
          vue.createVNode(MapView, vue.mergeProps(mapProps.value, {
            ref_key: "mapRef",
            ref: mapRef,
            message: vue.unref(lang).message,
            clickMessage: vue.unref(lang).clickMessage,
            searchPlaceholder: vue.unref(lang).placeholder,
            okText: vue.unref(lang).ok,
            mapKey: aMapKey.value,
            mode: _ctx.keywordMode ? "keyword" : _ctx.mode,
            onMapDone: handleMapDone,
            onDone: handleDone
          }), null, 16, ["message", "clickMessage", "searchPlaceholder", "okText", "mapKey", "mode"])
        ]),
        _: 2
      }, [
        vue.renderList(Object.keys(_ctx.$slots).filter((k) => "default" !== k), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["title", "modelValue", "class"]);
    };
  }
});
module.exports = _sfc_main;
