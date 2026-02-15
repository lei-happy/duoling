"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const util = require("../util");
const _hoisted_1 = { class: "ele-cron-panel-content" };
const _hoisted_2 = { class: "ele-cron-panel-item" };
const _hoisted_3 = { class: "ele-cron-panel-item-input" };
const _hoisted_4 = { class: "ele-cron-panel-item-input" };
const _hoisted_5 = { class: "ele-cron-panel-item" };
const _hoisted_6 = { class: "ele-cron-panel-item-input" };
const _hoisted_7 = { class: "ele-cron-panel-item-input" };
const _hoisted_8 = { class: "ele-cron-panel-options" };
const _hoisted_9 = { class: "ele-cron-panel-item" };
const _hoisted_10 = { class: "ele-cron-panel-item-input" };
const minValue = 1;
const maxValue = 31;
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  __name: "cron-day",
  props: {
    /** day */
    modelValue: String,
    /** 国际化 */
    lang: {
      type: Object,
      required: true
    }
  },
  emits: {
    "update:modelValue": (_day) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const {
      type,
      start,
      end,
      endMin,
      intervalStart,
      intervalStep,
      intervalStepMax,
      selections,
      getValue,
      parseValue
    } = util.useCron(minValue, maxValue);
    const workday = vue.ref(1);
    const updateModelValue = (day) => {
      emit("update:modelValue", day);
    };
    vue.watch(
      [type, start, end, intervalStart, intervalStep, selections, workday],
      () => {
        if (type.value === "workday") {
          updateModelValue(`${workday.value}W`);
          return;
        }
        if (type.value === "last") {
          updateModelValue("L");
          return;
        }
        if (type.value === "unset") {
          updateModelValue("?");
          return;
        }
        updateModelValue(getValue());
      },
      { deep: true, immediate: true }
    );
    vue.watch(
      () => props.modelValue,
      (day) => {
        if (day != null && day.endsWith("W")) {
          type.value = "workday";
          workday.value = Number(day.slice(0, -1));
          return;
        }
        if (day === "L") {
          type.value = "last";
          return;
        }
        if (day === "?") {
          type.value = "unset";
          return;
        }
        parseValue(day);
      },
      { immediate: true }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createVNode(vue.unref(elementPlus.ElRadioGroup), {
          modelValue: vue.unref(type),
          "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => vue.isRef(type) ? type.value = $event : null)
        }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "every",
              label: __props.lang.dayEvery
            }, null, 8, ["label"]),
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "range",
              class: "ele-cron-panel-item-wrapper"
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", _hoisted_2, [
                  vue.createElementVNode("div", null, vue.toDisplayString(__props.lang.dayRangeStart) + " ", 1),
                  vue.createElementVNode("div", _hoisted_3, [
                    vue.createVNode(vue.unref(elementPlus.ElInputNumber), {
                      modelValue: vue.unref(start),
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => vue.isRef(start) ? start.value = $event : null),
                      min: minValue,
                      max: maxValue - 1,
                      placeholder: "",
                      controlsPosition: "right"
                    }, null, 8, ["modelValue", "max"])
                  ]),
                  vue.createElementVNode("div", null, " " + vue.toDisplayString(__props.lang.dayRange) + " ", 1),
                  vue.createElementVNode("div", _hoisted_4, [
                    vue.createVNode(vue.unref(elementPlus.ElInputNumber), {
                      modelValue: vue.unref(end),
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => vue.isRef(end) ? end.value = $event : null),
                      min: vue.unref(endMin),
                      max: maxValue,
                      placeholder: "",
                      controlsPosition: "right"
                    }, null, 8, ["modelValue", "min"])
                  ]),
                  vue.createElementVNode("div", null, " " + vue.toDisplayString(__props.lang.dayRangeEnd), 1)
                ])
              ]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "interval",
              class: "ele-cron-panel-item-wrapper"
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", _hoisted_5, [
                  vue.createElementVNode("div", null, vue.toDisplayString(__props.lang.dayIntervalStart) + " ", 1),
                  vue.createElementVNode("div", _hoisted_6, [
                    vue.createVNode(vue.unref(elementPlus.ElInputNumber), {
                      modelValue: vue.unref(intervalStart),
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => vue.isRef(intervalStart) ? intervalStart.value = $event : null),
                      min: minValue,
                      max: maxValue - 1,
                      placeholder: "",
                      controlsPosition: "right"
                    }, null, 8, ["modelValue", "max"])
                  ]),
                  vue.createElementVNode("div", null, " " + vue.toDisplayString(__props.lang.dayInterval) + " ", 1),
                  vue.createElementVNode("div", _hoisted_7, [
                    vue.createVNode(vue.unref(elementPlus.ElInputNumber), {
                      modelValue: vue.unref(intervalStep),
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => vue.isRef(intervalStep) ? intervalStep.value = $event : null),
                      min: 1,
                      max: vue.unref(intervalStepMax),
                      placeholder: "",
                      controlsPosition: "right"
                    }, null, 8, ["modelValue", "max"])
                  ]),
                  vue.createElementVNode("div", null, " " + vue.toDisplayString(__props.lang.dayIntervalEnd), 1)
                ])
              ]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "specified",
              class: "ele-cron-panel-item-wrapper ele-cron-panel-options-wrapper"
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", null, vue.toDisplayString(__props.lang.daySpecified), 1),
                vue.createElementVNode("div", _hoisted_8, [
                  vue.createVNode(vue.unref(elementPlus.ElCheckboxGroup), {
                    modelValue: vue.unref(selections),
                    "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => vue.isRef(selections) ? selections.value = $event : null)
                  }, {
                    default: vue.withCtx(() => [
                      (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(maxValue + 1, (item) => {
                        return vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: item }, [
                          item - 1 >= minValue ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCheckbox), {
                            key: 0,
                            value: item - 1,
                            label: item - 1
                          }, null, 8, ["value", "label"])) : vue.createCommentVNode("", true)
                        ], 64);
                      }), 128))
                    ]),
                    _: 1
                  }, 8, ["modelValue"])
                ])
              ]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "workday",
              class: "ele-cron-panel-item-wrapper"
            }, {
              default: vue.withCtx(() => [
                vue.createElementVNode("div", _hoisted_9, [
                  vue.createElementVNode("div", null, vue.toDisplayString(__props.lang.dayWorkday) + " ", 1),
                  vue.createElementVNode("div", _hoisted_10, [
                    vue.createVNode(vue.unref(elementPlus.ElInputNumber), {
                      modelValue: workday.value,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => workday.value = $event),
                      min: minValue,
                      max: maxValue,
                      placeholder: "",
                      controlsPosition: "right"
                    }, null, 8, ["modelValue"])
                  ]),
                  vue.createElementVNode("div", null, " " + vue.toDisplayString(__props.lang.dayWorkdayText), 1)
                ])
              ]),
              _: 1
            }),
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "last",
              label: __props.lang.dayLast
            }, null, 8, ["label"]),
            vue.createVNode(vue.unref(elementPlus.ElRadio), {
              value: "unset",
              label: __props.lang.dayUnset
            }, null, 8, ["label"])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ]);
    };
  }
});
module.exports = _sfc_main;
