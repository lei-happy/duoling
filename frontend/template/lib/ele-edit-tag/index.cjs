"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const EleTooltip = require("../ele-tooltip/index");
const index = require("../icons/index");
const util = require("../ele-basic-select/util");
const props = require("./props");
const _hoisted_1 = { key: 0 };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleEditTag" },
  __name: "index",
  props: props.editTagProps,
  emits: props.editTagEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const { validateChange } = util.useFormValidate();
    const inputTagRef = vue.ref(null);
    const inputRef = vue.ref(null);
    const isEdit = vue.ref(false);
    const inputValue = vue.ref("");
    const errorMessage = vue.ref("");
    const loading = vue.ref(false);
    const tooltipVisible = vue.ref(false);
    const isDeactivated = vue.ref(false);
    const updateModelValue = (modelValue) => {
      emit("update:modelValue", modelValue);
      validateChange();
      emit("change", modelValue);
    };
    const addTag = (value) => {
      tooltipVisible.value = false;
      isEdit.value = false;
      updateInputValue("");
      errorMessage.value = "";
      loading.value = false;
      if (value) {
        const temp = props2.modelValue ? [...props2.modelValue] : [];
        temp.push(value);
        updateModelValue(temp);
      }
    };
    const removeTag = (index2) => {
      if (!props2.modelValue) {
        return;
      }
      const temp = [...props2.modelValue];
      temp.splice(index2, 1);
      updateModelValue(temp);
    };
    const updateInputValue = (value) => {
      inputValue.value = value;
    };
    const focusInput = () => {
      setTimeout(() => {
        inputRef.value && inputRef.value.focus();
      }, 0);
    };
    const handleAddClick = () => {
      if (props2.disabled) {
        return;
      }
      tooltipVisible.value = false;
      errorMessage.value = "";
      isEdit.value = true;
      vue.nextTick(() => {
        focusInput();
      });
    };
    const handleTagClose = (index2, item) => {
      if (typeof props2.beforeRemove !== "function") {
        removeTag(index2);
        return;
      }
      props2.beforeRemove(index2, item).then(() => {
        removeTag(index2);
      }).catch(() => {
      });
    };
    const handleTagClick = (index2, item) => {
      emit("itemClick", index2, item);
    };
    const handleInputChange = () => {
      if (!inputValue.value) {
        return;
      }
      if (typeof props2.validator !== "function") {
        addTag(inputValue.value);
        return;
      }
      loading.value = true;
      props2.validator(inputValue.value).then(() => {
        addTag(inputValue.value);
      }).catch((e) => {
        loading.value = false;
        if (e && e.message != null && e.message !== "") {
          errorMessage.value = e.message;
          if (isEdit.value && !isDeactivated.value) {
            tooltipVisible.value = true;
          }
        }
        vue.nextTick(() => {
          focusInput();
        });
      });
    };
    const handleInputBlur = () => {
      tooltipVisible.value = false;
      if (!inputValue.value) {
        isEdit.value = false;
        errorMessage.value = "";
      }
    };
    const handleInputFocus = () => {
      if (errorMessage.value && !tooltipVisible.value && isEdit.value && !isDeactivated.value) {
        tooltipVisible.value = true;
      }
    };
    vue.onDeactivated(() => {
      isDeactivated.value = true;
      tooltipVisible.value = false;
    });
    vue.onActivated(() => {
      isDeactivated.value = false;
    });
    __expose({
      inputTagRef,
      inputRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-edit-tag", [
          { "is-large": _ctx.size === "large" },
          { "is-small": _ctx.size === "small" },
          { "is-disabled": _ctx.disabled },
          { "is-readonly": _ctx.readonly }
        ]])
      }, [
        _ctx.modelValue ? (vue.openBlock(true), vue.createElementBlock(vue.Fragment, { key: 0 }, vue.renderList(_ctx.modelValue, (item, index2) => {
          return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTag), {
            key: `${index2}-${item}`,
            hit: _ctx.hit,
            type: _ctx.type,
            color: _ctx.color,
            size: _ctx.size,
            effect: _ctx.effect,
            round: _ctx.round,
            closable: _ctx.readonly || _ctx.disabled ? false : true,
            disableTransitions: true,
            style: vue.normalizeStyle(_ctx.itemStyle),
            onClose: ($event) => handleTagClose(index2, item),
            onClick: ($event) => handleTagClick(index2, item)
          }, {
            default: vue.withCtx(() => [
              vue.createTextVNode(vue.toDisplayString(item), 1)
            ]),
            _: 2
          }, 1032, ["hit", "type", "color", "size", "effect", "round", "closable", "style", "onClose", "onClick"]);
        }), 128)) : vue.createCommentVNode("", true),
        !_ctx.readonly ? vue.withDirectives((vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTag), {
          key: 1,
          hit: _ctx.hit,
          type: "info",
          size: _ctx.size,
          round: _ctx.round,
          disableTransitions: true,
          class: "ele-edit-tag-add",
          style: vue.normalizeStyle(_ctx.buttonStyle),
          onClick: handleAddClick
        }, {
          default: vue.withCtx(() => [
            vue.renderSlot(_ctx.$slots, "placeholder", {}, () => [
              _ctx.placeholder ? (vue.openBlock(), vue.createElementBlock("span", _hoisted_1, vue.toDisplayString(_ctx.placeholder), 1)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                key: 1,
                class: "ele-edit-tag-add-icon"
              }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.PlusOutlined))
                ]),
                _: 1
              }))
            ])
          ]),
          _: 3
        }, 8, ["hit", "size", "round", "style"])), [
          [vue.vShow, !isEdit.value]
        ]) : vue.createCommentVNode("", true),
        !_ctx.readonly ? vue.withDirectives((vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTag), {
          key: 2,
          ref_key: "inputTagRef",
          ref: inputTagRef,
          size: _ctx.size,
          round: _ctx.round,
          disableTransitions: true,
          class: vue.normalizeClass(["ele-edit-tag-input", { "is-error": !!errorMessage.value }]),
          style: vue.normalizeStyle(_ctx.inputTagStyle)
        }, {
          default: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElInput), {
              ref_key: "inputRef",
              ref: inputRef,
              disabled: loading.value,
              modelValue: inputValue.value,
              "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => inputValue.value = $event),
              validateEvent: false,
              style: vue.normalizeStyle(_ctx.inputStyle),
              onChange: handleInputChange,
              onBlur: handleInputBlur,
              onFocus: handleInputFocus
            }, {
              suffix: vue.withCtx(() => [
                loading.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
                  key: 0,
                  class: "is-loading"
                }, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.LoadingOutlined))
                  ]),
                  _: 1
                })) : vue.createCommentVNode("", true)
              ]),
              _: 1
            }, 8, ["disabled", "modelValue", "style"])
          ]),
          _: 1
        }, 8, ["size", "round", "class", "style"])), [
          [vue.vShow, isEdit.value]
        ]) : vue.createCommentVNode("", true),
        vue.createVNode(EleTooltip, vue.mergeProps({
          offset: 7,
          hideAfter: 0,
          trigger: "click",
          triggerKeys: [],
          disabled: !tooltipVisible.value
        }, _ctx.tooltipProps || {}, {
          virtualTriggering: true,
          virtualRef: inputTagRef.value ? inputTagRef.value.$el : void 0,
          content: errorMessage.value,
          visible: tooltipVisible.value
        }), null, 16, ["disabled", "virtualRef", "content", "visible"])
      ], 2);
    };
  }
});
module.exports = _sfc_main;
