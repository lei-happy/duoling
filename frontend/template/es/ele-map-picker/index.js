import { defineComponent, ref, computed, watch, createBlock, openBlock, mergeProps, unref, createSlots, withCtx, createVNode, renderList, renderSlot, normalizeProps, guardReactiveProps } from "vue";
import { pick } from "../utils/common";
import { useLocale } from "../ele-config-provider/receiver";
import { useResponsive } from "../ele-pro-layout/util";
import EleModal from "../ele-modal/index";
import MapView from "./components/map-view";
import { mapPickerEmits, mapPickerProps, mapPropKeys } from "./props";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "EleMapPicker" },
  __name: "index",
  props: mapPickerProps,
  emits: mapPickerEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const { lang, globalConfig } = useLocale("map", props);
    const isResponsive = useResponsive(props);
    const mapRef = ref(null);
    const aMapKey = computed(() => props.mapKey || globalConfig.mapKey);
    const mapProps = computed(() => {
      return pick(props, mapPropKeys);
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
    watch(
      () => props.modelValue,
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
      return openBlock(), createBlock(EleModal, mergeProps({
        width: "740px",
        title: unref(lang).title
      }, _ctx.modalProps || {}, {
        modelValue: _ctx.modelValue,
        class: ["ele-map-picker", { "is-responsive": unref(isResponsive) }],
        "onUpdate:modelValue": updateModelValue
      }), createSlots({
        default: withCtx(() => [
          createVNode(MapView, mergeProps(mapProps.value, {
            ref_key: "mapRef",
            ref: mapRef,
            message: unref(lang).message,
            clickMessage: unref(lang).clickMessage,
            searchPlaceholder: unref(lang).placeholder,
            okText: unref(lang).ok,
            mapKey: aMapKey.value,
            mode: _ctx.keywordMode ? "keyword" : _ctx.mode,
            onMapDone: handleMapDone,
            onDone: handleDone
          }), null, 16, ["message", "clickMessage", "searchPlaceholder", "okText", "mapKey", "mode"])
        ]),
        _: 2
      }, [
        renderList(Object.keys(_ctx.$slots).filter((k) => "default" !== k), (name) => {
          return {
            name,
            fn: withCtx((slotProps) => [
              renderSlot(_ctx.$slots, name, normalizeProps(guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["title", "modelValue", "class"]);
    };
  }
});
export {
  _sfc_main as default
};
