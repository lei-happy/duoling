"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const receiver = require("../ele-config-provider/receiver");
const EleModal = require("../ele-modal/index");
const EleCronPanel = require("../ele-cron-panel/index");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCronBuilder" },
  __name: "index",
  props: props.cronBuilderProps,
  emits: props.cronBuilderEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("cronBuilder", props2);
    const cronPanelRef = vue.ref(null);
    const cronModel = vue.ref("");
    const updateModelValue = (value) => {
      emit("update:modelValue", value);
    };
    const updateCronModel = (value) => {
      if (cronModel.value !== value) {
        cronModel.value = value;
        if (props2.cron !== cronModel.value) {
          emit("update:cron", cronModel.value);
        }
      }
    };
    const hideCronList = () => {
      cronPanelRef.value?.hideCronList?.();
    };
    const handleCancel = () => {
      hideCronList();
      updateModelValue(false);
    };
    const handleConfirm = () => {
      hideCronList();
      emit("done", cronModel.value);
    };
    const handleClosed = () => {
      hideCronList();
    };
    vue.watch(
      () => props2.cron,
      (value) => {
        updateCronModel(value);
      },
      { immediate: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleModal, vue.mergeProps({
        width: 832,
        title: _ctx.title ?? vue.unref(lang).title,
        position: "center",
        class: "ele-cron-builder"
      }, _ctx.modalProps || {}, {
        modelValue: _ctx.modelValue,
        "onUpdate:modelValue": updateModelValue,
        onClosed: handleClosed
      }), vue.createSlots({
        footer: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "footer"),
          vue.createVNode(vue.unref(elementPlus.ElButton), { onClick: handleCancel }, {
            default: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(vue.unref(lang).cancel), 1)
            ]),
            _: 1
          }),
          vue.createVNode(vue.unref(elementPlus.ElButton), {
            type: "primary",
            onClick: handleConfirm
          }, {
            default: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(vue.unref(lang).confirm), 1)
            ]),
            _: 1
          })
        ]),
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "default"),
          vue.createVNode(EleCronPanel, {
            ref_key: "cronPanelRef",
            ref: cronPanelRef,
            modelValue: cronModel.value,
            "onUpdate:modelValue": updateCronModel
          }, null, 8, ["modelValue"])
        ]),
        _: 2
      }, [
        vue.renderList(Object.keys(_ctx.$slots).filter(
          (k) => ["default", "footer"].includes(k)
        ), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1040, ["title", "modelValue"]);
    };
  }
});
module.exports = _sfc_main;
