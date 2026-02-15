"use strict";
const vue = require("vue");
const receiver = require("../ele-config-provider/receiver");
const EleTabs = require("../ele-tabs/index");
const CronSecond = require("./components/cron-second");
const CronMinute = require("./components/cron-minute");
const CronHour = require("./components/cron-hour");
const CronDay = require("./components/cron-day");
const CronMonth = require("./components/cron-month");
const CronWeek = require("./components/cron-week");
const CronYear = require("./components/cron-year");
const util = require("./util");
const props = require("./props");
const _hoisted_1 = { class: "ele-cron-panel" };
const _hoisted_2 = { class: "ele-cron-panel-main" };
const _hoisted_3 = { class: "ele-cron-panel-extra" };
const _hoisted_4 = { class: "ele-cron-panel-extra-item" };
const _hoisted_5 = { class: "ele-cron-panel-extra-header" };
const _hoisted_6 = { class: "ele-cron-panel-extra-body" };
const _hoisted_7 = { class: "ele-cron-panel-result" };
const _hoisted_8 = { class: "ele-cron-panel-result-item" };
const _hoisted_9 = { class: "ele-cron-panel-result-title" };
const _hoisted_10 = { class: "ele-cron-panel-result-text" };
const _hoisted_11 = { class: "ele-cron-panel-result-item" };
const _hoisted_12 = { class: "ele-cron-panel-result-title" };
const _hoisted_13 = { class: "ele-cron-panel-result-text" };
const _hoisted_14 = { class: "ele-cron-panel-result-item" };
const _hoisted_15 = { class: "ele-cron-panel-result-title" };
const _hoisted_16 = { class: "ele-cron-panel-result-text" };
const _hoisted_17 = { class: "ele-cron-panel-result-item" };
const _hoisted_18 = { class: "ele-cron-panel-result-title" };
const _hoisted_19 = { class: "ele-cron-panel-result-text" };
const _hoisted_20 = { class: "ele-cron-panel-result-item" };
const _hoisted_21 = { class: "ele-cron-panel-result-title" };
const _hoisted_22 = { class: "ele-cron-panel-result-text" };
const _hoisted_23 = { class: "ele-cron-panel-result-item" };
const _hoisted_24 = { class: "ele-cron-panel-result-title" };
const _hoisted_25 = { class: "ele-cron-panel-result-text" };
const _hoisted_26 = { class: "ele-cron-panel-result-item" };
const _hoisted_27 = { class: "ele-cron-panel-result-title" };
const _hoisted_28 = { class: "ele-cron-panel-result-text" };
const _hoisted_29 = { class: "ele-cron-panel-result" };
const _hoisted_30 = { class: "ele-cron-panel-result-item" };
const _hoisted_31 = { class: "ele-cron-panel-result-title" };
const _hoisted_32 = { class: "ele-cron-panel-result-text ele-cron-panel-result-value" };
const _hoisted_33 = { class: "ele-cron-panel-extra-item" };
const _hoisted_34 = { class: "ele-cron-panel-extra-header" };
const _hoisted_35 = { class: "ele-cron-panel-extra-body" };
const _hoisted_36 = { class: "ele-cron-panel-test" };
const _hoisted_37 = ["onClick"];
const _hoisted_38 = { class: "ele-cron-panel-list-item-value" };
const _hoisted_39 = { class: "ele-cron-panel-list-item-label" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCronPanel" },
  __name: "index",
  props: props.cronPanelProps,
  emits: props.cronPanelEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("cronPanel", props2);
    const second = vue.ref("*");
    const minute = vue.ref("*");
    const hour = vue.ref("*");
    const day = vue.ref("*");
    const month = vue.ref("*");
    const week = vue.ref("?");
    const year = vue.ref("");
    const resultItems = vue.ref([]);
    const tabActive = vue.ref("second");
    const tabItems = vue.computed(() => {
      return [
        { name: "second", label: lang.value.second },
        { name: "minute", label: lang.value.minute },
        { name: "hour", label: lang.value.hour },
        { name: "day", label: lang.value.day },
        { name: "month", label: lang.value.month },
        { name: "week", label: lang.value.week },
        { name: "year", label: lang.value.year }
      ];
    });
    const updateModelValue = (value) => {
      if (props2.modelValue !== value) {
        emit("update:modelValue", value);
      }
    };
    const updateCron = () => {
      const values = [
        second.value,
        minute.value,
        hour.value,
        day.value,
        month.value,
        week.value
      ];
      if (year.value != null && year.value !== "") {
        values.push(year.value);
      }
      const cron = values.join(" ");
      updateModelValue(cron);
      return cron;
    };
    const updatePanel = (cron) => {
      if (!cron) {
        tabActive.value = "second";
        second.value = "*";
        minute.value = "*";
        hour.value = "*";
        day.value = "*";
        month.value = "*";
        week.value = "?";
        year.value = "";
        const str = updateCron();
        resultItems.value = util.getResultItems(
          str,
          lang.value.resultNoData,
          lang.value.resultNoMore
        );
        return;
      }
      const [s, m, h, d, m2, w, y] = cron.split(" ");
      second.value = s;
      minute.value = m;
      hour.value = h;
      day.value = d;
      month.value = m2;
      week.value = w;
      year.value = y || "";
      resultItems.value = util.getResultItems(
        cron,
        lang.value.resultNoData,
        lang.value.resultNoMore
      );
    };
    vue.watch(hour, (h) => {
      if (h !== "*" && second.value === "*") {
        second.value = "0";
      }
      if (h !== "*" && minute.value === "*") {
        minute.value = "0";
      }
    });
    vue.watch(day, (d) => {
      if (d !== "?" && week.value !== "?") {
        week.value = "?";
      }
    });
    vue.watch(week, (w) => {
      if (w !== "?" && day.value !== "?") {
        day.value = "?";
      }
    });
    vue.watch([second, minute, hour, day, month, week, year], () => {
      updateCron();
    });
    vue.watch(
      () => props2.modelValue,
      (cron) => {
        updatePanel(cron);
      }
    );
    vue.watch(lang, () => {
      resultItems.value = util.getResultItems(
        props2.modelValue,
        lang.value.resultNoData,
        lang.value.resultNoMore
      );
    });
    const cronListVisible = vue.ref(false);
    const cronList = vue.computed(() => {
      return [
        { cron: "0 * * * * ?", label: lang.value.common01 },
        { cron: "0 0 * * * ?", label: lang.value.common02 },
        { cron: "0 0/30 * * * ?", label: lang.value.common03 },
        { cron: "0 0/30 8-9 * * ?", label: lang.value.common04 },
        { cron: "0 0 0 * * ?", label: lang.value.common05 },
        { cron: "0 30 8 * * ?", label: lang.value.common06 },
        { cron: "0 0 8,14,19 * * ?", label: lang.value.common07 },
        { cron: "0 0 0 1 * ?", label: lang.value.common08 },
        { cron: "0 0 2 1 * ?", label: lang.value.common09 },
        { cron: "0 30 8 15 * ?", label: lang.value.common10 },
        { cron: "0 0 0 L * ?", label: lang.value.common11 },
        { cron: "0 30 8 L * ?", label: lang.value.common12 },
        { cron: "0 30 8 ? * 6L", label: lang.value.common13 },
        { cron: "0 0 0 ? * 1", label: lang.value.common14 },
        { cron: "0 0 8 ? * 2-4", label: lang.value.common15 },
        { cron: "0 0 0 1 10 ? 2025-2028", label: lang.value.common16 }
      ];
    });
    const handleItemClick = (item) => {
      hideCronList();
      updateModelValue(item.cron);
    };
    const openCronList = () => {
      cronListVisible.value = true;
    };
    const hideCronList = () => {
      cronListVisible.value = false;
    };
    __expose({ hideCronList });
    if (props2.modelValue) {
      updatePanel(props2.modelValue);
    } else {
      updateCron();
    }
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        vue.createElementVNode("div", _hoisted_2, [
          vue.createVNode(EleTabs, {
            addable: true,
            type: "border-card",
            items: tabItems.value,
            modelValue: tabActive.value,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => tabActive.value = $event),
            onTabAdd: openCronList
          }, {
            second: vue.withCtx(() => [
              vue.createVNode(CronSecond, {
                modelValue: second.value,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => second.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            minute: vue.withCtx(() => [
              vue.createVNode(CronMinute, {
                modelValue: minute.value,
                "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => minute.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            hour: vue.withCtx(() => [
              vue.createVNode(CronHour, {
                modelValue: hour.value,
                "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => hour.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            day: vue.withCtx(() => [
              vue.createVNode(CronDay, {
                modelValue: day.value,
                "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => day.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            month: vue.withCtx(() => [
              vue.createVNode(CronMonth, {
                modelValue: month.value,
                "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => month.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            week: vue.withCtx(() => [
              vue.createVNode(CronWeek, {
                modelValue: week.value,
                "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => week.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            year: vue.withCtx(() => [
              vue.createVNode(CronYear, {
                modelValue: year.value,
                "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => year.value = $event),
                lang: vue.unref(lang)
              }, null, 8, ["modelValue", "lang"])
            ]),
            "add-icon": vue.withCtx(() => [
              vue.createElementVNode("div", null, vue.toDisplayString(vue.unref(lang).common), 1)
            ]),
            _: 1
          }, 8, ["items", "modelValue"])
        ]),
        vue.createElementVNode("div", _hoisted_3, [
          vue.createElementVNode("div", _hoisted_4, [
            vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(vue.unref(lang).result), 1),
            vue.createElementVNode("div", _hoisted_6, [
              vue.createElementVNode("div", _hoisted_7, [
                vue.createElementVNode("div", _hoisted_8, [
                  vue.createElementVNode("div", _hoisted_9, vue.toDisplayString(vue.unref(lang).resultSecond), 1),
                  vue.createElementVNode("div", _hoisted_10, vue.toDisplayString(second.value), 1)
                ]),
                vue.createElementVNode("div", _hoisted_11, [
                  vue.createElementVNode("div", _hoisted_12, vue.toDisplayString(vue.unref(lang).resultMinute), 1),
                  vue.createElementVNode("div", _hoisted_13, vue.toDisplayString(minute.value), 1)
                ]),
                vue.createElementVNode("div", _hoisted_14, [
                  vue.createElementVNode("div", _hoisted_15, vue.toDisplayString(vue.unref(lang).resultHour), 1),
                  vue.createElementVNode("div", _hoisted_16, vue.toDisplayString(hour.value), 1)
                ]),
                vue.createElementVNode("div", _hoisted_17, [
                  vue.createElementVNode("div", _hoisted_18, vue.toDisplayString(vue.unref(lang).resultDay), 1),
                  vue.createElementVNode("div", _hoisted_19, vue.toDisplayString(day.value), 1)
                ]),
                vue.createElementVNode("div", _hoisted_20, [
                  vue.createElementVNode("div", _hoisted_21, vue.toDisplayString(vue.unref(lang).resultMonth), 1),
                  vue.createElementVNode("div", _hoisted_22, vue.toDisplayString(month.value), 1)
                ]),
                vue.createElementVNode("div", _hoisted_23, [
                  vue.createElementVNode("div", _hoisted_24, vue.toDisplayString(vue.unref(lang).resultWeek), 1),
                  vue.createElementVNode("div", _hoisted_25, vue.toDisplayString(week.value), 1)
                ]),
                vue.createElementVNode("div", _hoisted_26, [
                  vue.createElementVNode("div", _hoisted_27, vue.toDisplayString(vue.unref(lang).resultYear), 1),
                  vue.createElementVNode("div", _hoisted_28, vue.toDisplayString(year.value), 1)
                ])
              ]),
              vue.createElementVNode("div", _hoisted_29, [
                vue.createElementVNode("div", _hoisted_30, [
                  vue.createElementVNode("div", _hoisted_31, vue.toDisplayString(vue.unref(lang).resultName), 1),
                  vue.createElementVNode("div", _hoisted_32, vue.toDisplayString(_ctx.modelValue), 1)
                ])
              ])
            ])
          ]),
          vue.createElementVNode("div", _hoisted_33, [
            vue.createElementVNode("div", _hoisted_34, vue.toDisplayString(vue.unref(lang).resultTest), 1),
            vue.createElementVNode("div", _hoisted_35, [
              vue.createElementVNode("ul", _hoisted_36, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(resultItems.value, (item) => {
                  return vue.openBlock(), vue.createElementBlock("li", {
                    key: item,
                    class: "ele-cron-panel-test-item"
                  }, vue.toDisplayString(item), 1);
                }), 128))
              ])
            ])
          ])
        ]),
        vue.createElementVNode("div", {
          class: vue.normalizeClass(["ele-cron-panel-list-mask", { "is-show": cronListVisible.value }]),
          onClick: hideCronList
        }, [
          vue.createElementVNode("div", {
            class: "ele-cron-panel-list-wrapper",
            onClick: _cache[8] || (_cache[8] = vue.withModifiers(() => {
            }, ["stop"]))
          }, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(cronList.value, (item) => {
              return vue.openBlock(), vue.createElementBlock("div", {
                key: item.cron,
                class: "ele-cron-panel-list-item",
                onClick: ($event) => handleItemClick(item)
              }, [
                vue.createElementVNode("div", _hoisted_38, vue.toDisplayString(item.cron), 1),
                vue.createElementVNode("div", _hoisted_39, vue.toDisplayString(item.label), 1)
              ], 8, _hoisted_37);
            }), 128))
          ])
        ], 2)
      ]);
    };
  }
});
module.exports = _sfc_main;
