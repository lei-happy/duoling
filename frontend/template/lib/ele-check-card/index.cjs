"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const hook = require("../utils/hook");
const util = require("../ele-basic-select/util");
const CardItem = require("./components/card-item");
const props = require("./props");
const _hoisted_1 = { class: "ele-check-card-group" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCheckCard" },
  __name: "index",
  props: props.checkCardProps,
  emits: props.checkCardEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { validateChange } = util.useFormValidate();
    const { optionData, reloadOptions } = hook.useProOptions(
      props2,
      "items"
    );
    const isChecked = (item) => {
      if (props2.modelValue == null || item.value == null) {
        return false;
      }
      if (!props2.multiple) {
        return props2.modelValue === item.value;
      }
      if (!Array.isArray(props2.modelValue)) {
        return false;
      }
      return props2.modelValue.includes(item.value);
    };
    const updateModelValue = (modelValue) => {
      if (util.valueIsChanged(modelValue, props2.modelValue, props2.multiple)) {
        emit("update:modelValue", modelValue);
        validateChange();
        emit("change", modelValue);
      }
    };
    const handleItemClick = (item) => {
      if (props2.disabled || item.disabled) {
        return;
      }
      if (!props2.multiple) {
        if (props2.allowUncheck && !util.isEmptyValue(props2.modelValue) && props2.modelValue === item.value) {
          updateModelValue(null);
          return;
        }
        updateModelValue(item.value);
        return;
      }
      if (!isChecked(item)) {
        if (props2.modelValue == null || !Array.isArray(props2.modelValue)) {
          updateModelValue(item.value == null ? [] : [item.value]);
          return;
        }
        const temp = [...props2.modelValue];
        if (item.value != null) {
          temp.push(item.value);
        }
        updateModelValue(temp);
        return;
      }
      if (props2.modelValue == null || !Array.isArray(props2.modelValue)) {
        updateModelValue([]);
        return;
      }
      updateModelValue(props2.modelValue.filter((v) => v !== item.value));
    };
    __expose({
      reloadOptions
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", _hoisted_1, [
        _ctx.row ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElRow), vue.normalizeProps(vue.mergeProps({ key: 0 }, _ctx.row === true ? {} : _ctx.row)), {
          default: vue.withCtx(() => [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(vue.unref(optionData), (item, index) => {
              return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCol), vue.mergeProps({
                key: `${index}-${item.value}`
              }, { ref_for: true }, item.col || {}), {
                default: vue.withCtx(() => [
                  vue.createVNode(CardItem, {
                    item,
                    checked: isChecked(item),
                    disabled: _ctx.disabled || item.disabled,
                    bordered: _ctx.bordered || item.bordered,
                    arrow: _ctx.arrow,
                    arrowStyle: _ctx.arrowStyle,
                    style: vue.normalizeStyle([_ctx.itemStyle, item.style]),
                    class: vue.normalizeClass([_ctx.itemClass, item.class]),
                    onClick: ($event) => handleItemClick(item)
                  }, {
                    default: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, "item", vue.mergeProps({ ref_for: true }, slotProps || {}), () => [
                        vue.createTextVNode(vue.toDisplayString(item.label ?? item.value), 1)
                      ])
                    ]),
                    _: 2
                  }, 1032, ["item", "checked", "disabled", "bordered", "arrow", "arrowStyle", "style", "class", "onClick"])
                ]),
                _: 2
              }, 1040);
            }), 128))
          ]),
          _: 3
        }, 16)) : (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 1 }, vue.renderList(vue.unref(optionData), (item, index) => {
          return vue.openBlock(), vue.createBlock(CardItem, {
            key: item.key ?? `${index}-${item.value}`,
            item,
            checked: isChecked(item),
            disabled: _ctx.disabled || item.disabled,
            bordered: _ctx.bordered || item.bordered,
            arrow: _ctx.arrow,
            arrowStyle: _ctx.arrowStyle,
            style: vue.normalizeStyle([_ctx.itemStyle, item.style]),
            class: vue.normalizeClass([_ctx.itemClass, item.class]),
            onClick: ($event) => handleItemClick(item)
          }, {
            default: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, "item", vue.mergeProps({ ref_for: true }, slotProps || {}), () => [
                vue.createTextVNode(vue.toDisplayString(item.label ?? item.value), 1)
              ])
            ]),
            _: 2
          }, 1032, ["item", "checked", "disabled", "bordered", "arrow", "arrowStyle", "style", "class", "onClick"]);
        }), 128))
      ]);
    };
  }
});
module.exports = _sfc_main;
