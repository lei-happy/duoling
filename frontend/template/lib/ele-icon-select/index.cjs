"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const receiver = require("../ele-config-provider/receiver");
const util$1 = require("../ele-pro-layout/util");
const EleBasicSelect = require("../ele-basic-select/index");
const util = require("../ele-basic-select/util");
const index = require("../icons/index");
const IconGrid = require("./components/icon-grid");
const props = require("./props");
const _hoisted_1 = ["onClick"];
const _hoisted_2 = { class: "ele-icon-select-main" };
const _hoisted_3 = ["onClick"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleIconSelect" },
  __name: "index",
  props: props.iconSelectProps,
  emits: props.iconSelectEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const ownSlots = ["default", "icon", "tabLeftExtra", "tabRightExtra"];
    const props2 = __props;
    const emit = __emit;
    const { lang } = receiver.useLocale("iconSelect", props2);
    const { validateChange } = util.useFormValidate();
    const isResponsive = util$1.useResponsive(props2);
    const selectRef = vue.ref(null);
    const selectVisible = vue.ref(false);
    const tabs = vue.ref([]);
    const tabActive = vue.ref();
    const menus = vue.ref([]);
    const menuActive = vue.ref();
    const icons = vue.ref([]);
    const keywords = vue.ref("");
    const tabBar = vue.computed(() => {
      if (!tabs.value || !tabs.value.length) {
        return false;
      }
      if (props2.hideOnSingleTab && tabs.value.length === 1) {
        return false;
      }
      return true;
    });
    const showFilterInput = vue.computed(() => {
      if (props2.filterable === true && props2.popperType !== "popper") {
        return true;
      }
      return props2.filterable === "popper";
    });
    const selectPopperClass = vue.computed(() => {
      const classes = ["ele-icon-select-popper"];
      if (props2.popperType === "default") {
        classes.push("is-icon-select-default");
      }
      if (props2.popperType === "modal" && (tabBar.value || showFilterInput.value || menus.value?.length)) {
        classes.push("ele-modal-show-header-border");
      }
      if (isResponsive.value && props2.popperType === "popper") {
        classes.push("is-icon-select-responsive");
      }
      if (props2.popperClass) {
        classes.push(props2.popperClass);
      }
      return classes.join(" ");
    });
    const updatePopover = () => {
      selectRef.value && selectRef.value.updatePopper();
    };
    const initData = () => {
      if (props2.data == null || !props2.data.length || typeof props2.data[0] === "string") {
        tabs.value = [];
        menus.value = [];
        tabActive.value = void 0;
        menuActive.value = void 0;
        icons.value = filterData(props2.data);
        return;
      }
      tabs.value = props2.data.map(
        (d) => d.title
      );
      if (tabActive.value == null || tabActive.value >= tabs.value.length) {
        tabActive.value = 0;
      }
      const data = props2.data[tabActive.value];
      if (typeof data !== "string" && data.children != null && data.children.length) {
        menus.value = data.children.map((d) => d.title);
        if (menuActive.value == null || menuActive.value >= menus.value.length) {
          menuActive.value = 0;
        }
        icons.value = filterData(data.children[menuActive.value].icons);
        return;
      }
      menus.value = [];
      menuActive.value = void 0;
      icons.value = typeof data !== "string" ? filterData(data.icons) : [];
    };
    const filterData = (data) => {
      if (!data) {
        return [];
      }
      if (!keywords.value) {
        return data;
      }
      const keyword = keywords.value.toLowerCase();
      return data.filter((t) => t.toLowerCase().includes(keyword));
    };
    const updateVisible = (visible) => {
      if (visible) {
        handleSelectFilter("");
      }
      if (selectVisible.value !== visible) {
        selectVisible.value = visible;
        emit("visibleChange", visible);
      }
    };
    const updateModelValue = (modelValue) => {
      if (util.valueIsChanged(modelValue, props2.modelValue)) {
        emit("update:modelValue", modelValue);
        validateChange();
        emit("change", modelValue);
      }
    };
    const handleSelectClear = () => {
      updateModelValue(null);
      updateVisible(false);
      emit("clear");
    };
    const handleSelectFocus = (e) => {
      emit("focus", e);
    };
    const handleSelectBlur = (e) => {
      emit("blur", e);
    };
    const handleSelectFilter = (value) => {
      if (keywords.value !== value) {
        keywords.value = value;
      }
      initData();
      if (!props2.data?.length || icons.value.length) {
        return;
      }
      for (let i = 0; i < props2.data.length; i++) {
        const d = props2.data[i];
        if (typeof d === "string") {
          return;
        }
        const keyword = keywords.value.toLowerCase();
        if (d.children != null && d.children.length) {
          for (let j = 0; j < d.children.length; j++) {
            const icons2 = d.children[j].icons;
            if (icons2 && icons2.some((t) => t.toLowerCase().includes(keyword))) {
              menuActive.value = j;
              tabActive.value = i;
              initData();
              return;
            }
          }
        } else if (d.icons != null && d.icons.some((t) => t.toLowerCase().includes(keyword))) {
          tabActive.value = i;
          initData();
          return;
        }
      }
    };
    const handleTabClick = (index2) => {
      tabActive.value = index2;
      initData();
    };
    const handleMenuClick = (index2) => {
      menuActive.value = index2;
      initData();
    };
    const handleIconSelect = (icon) => {
      updateModelValue(icon);
      updateVisible(false);
    };
    vue.watch(
      () => props2.data,
      () => {
        initData();
      },
      {
        immediate: true,
        deep: true
      }
    );
    __expose({
      selectRef,
      updatePopover
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleBasicSelect, {
        ref_key: "selectRef",
        ref: selectRef,
        value: _ctx.modelValue,
        multiple: false,
        disabled: _ctx.disabled,
        size: _ctx.size,
        clearable: _ctx.clearable,
        placeholder: _ctx.placeholder,
        automaticDropdown: _ctx.automaticDropdown,
        filterable: typeof _ctx.filterable === "boolean" ? _ctx.filterable : false,
        teleported: _ctx.teleported,
        persistent: _ctx.persistent,
        placement: _ctx.placement,
        transition: _ctx.transition,
        popperOptions: _ctx.popperOptions,
        selectClass: "is-icon-select",
        selectStyle: _ctx.selectStyle,
        inputStyle: _ctx.inputStyle,
        selectTagsStyle: _ctx.selectTagsStyle,
        popperClass: selectPopperClass.value,
        popperWidth: _ctx.popperWidth,
        popperHeight: _ctx.popperHeight,
        popperType: _ctx.popperType,
        popperProps: _ctx.popperProps,
        popperSlots: _ctx.popperSlots,
        popperTitle: vue.unref(lang).title,
        responsive: vue.unref(isResponsive),
        selectedLabel: _ctx.modelValue,
        visible: selectVisible.value,
        "onUpdate:visible": updateVisible,
        onFilterChange: handleSelectFilter,
        onClear: handleSelectClear,
        onFocus: handleSelectFocus,
        onBlur: handleSelectBlur
      }, vue.createSlots({
        default: vue.withCtx(() => [
          tabBar.value || showFilterInput.value ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 0,
            class: "ele-icon-select-header",
            style: vue.normalizeStyle(_ctx.headerStyle)
          }, [
            vue.renderSlot(_ctx.$slots, "tabLeftExtra"),
            tabBar.value ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-icon-select-tabs",
              style: vue.normalizeStyle(_ctx.tabsStyle)
            }, [
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(tabs.value, (t, i) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: `${i}-${t}`,
                  class: vue.normalizeClass(["ele-icon-select-tab", { "is-active": i === tabActive.value }]),
                  onClick: ($event) => handleTabClick(i)
                }, vue.toDisplayString(t), 11, _hoisted_1);
              }), 128))
            ], 4)) : vue.createCommentVNode("", true),
            showFilterInput.value ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 1,
              class: "ele-icon-select-search",
              style: vue.normalizeStyle(_ctx.searchStyle)
            }, [
              vue.createVNode(vue.unref(elementPlus.ElInput), {
                size: "small",
                clearable: true,
                modelValue: keywords.value,
                validateEvent: false,
                prefixIcon: vue.unref(index.SearchOutlined),
                placeholder: _ctx.filterPlaceholder ?? vue.unref(lang).searchPlaceholder,
                "onUpdate:modelValue": handleSelectFilter
              }, null, 8, ["modelValue", "prefixIcon", "placeholder"])
            ], 4)) : vue.createCommentVNode("", true),
            vue.renderSlot(_ctx.$slots, "tabRightExtra")
          ], 4)) : vue.createCommentVNode("", true),
          vue.createElementVNode("div", _hoisted_2, [
            menus.value && menus.value.length ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: "ele-icon-select-menus",
              style: vue.normalizeStyle(_ctx.menusStyle)
            }, [
              (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(menus.value, (m, i) => {
                return vue.openBlock(), vue.createElementBlock("div", {
                  key: `${i}-${m}`,
                  class: vue.normalizeClass(["ele-icon-select-menu", { "is-active": i === menuActive.value }]),
                  onClick: ($event) => handleMenuClick(i)
                }, vue.toDisplayString(m), 11, _hoisted_3);
              }), 128))
            ], 4)) : vue.createCommentVNode("", true),
            vue.createVNode(IconGrid, {
              data: icons.value,
              icon: _ctx.modelValue,
              emptyProps: _ctx.emptyProps,
              tooltip: _ctx.tooltip,
              tooltipProps: _ctx.tooltipProps,
              popperVisible: selectVisible.value,
              gridStyle: _ctx.gridStyle,
              itemStyle: _ctx.itemStyle,
              popperType: _ctx.popperType,
              style: vue.normalizeStyle(_ctx.bodyStyle),
              onSelect: handleIconSelect
            }, vue.createSlots({ _: 2 }, [
              _ctx.$slots.icon ? {
                name: "icon",
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, "icon", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ]),
                key: "0"
              } : void 0
            ]), 1032, ["data", "icon", "emptyProps", "tooltip", "tooltipProps", "popperVisible", "gridStyle", "itemStyle", "popperType", "style"])
          ])
        ]),
        _: 2
      }, [
        vue.renderList(Object.keys(_ctx.$slots).filter((k) => !ownSlots.includes(k)), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        }),
        _ctx.modelValue && _ctx.$slots.icon ? {
          name: "prefix",
          fn: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "icon", {
              icon: _ctx.modelValue,
              prefix: true
            })
          ]),
          key: "0"
        } : void 0
      ]), 1032, ["value", "disabled", "size", "clearable", "placeholder", "automaticDropdown", "filterable", "teleported", "persistent", "placement", "transition", "popperOptions", "selectStyle", "inputStyle", "selectTagsStyle", "popperClass", "popperWidth", "popperHeight", "popperType", "popperProps", "popperSlots", "popperTitle", "responsive", "selectedLabel", "visible"]);
    };
  }
});
module.exports = _sfc_main;
