"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const props = require("../props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "SelectView" },
  __name: "select-view",
  props: props.basicSelectProps,
  emits: {
    ...props.basicSelectEmits,
    /** 输入框点击事件 */
    inputClick: (_e) => true,
    /** 容器点击事件 */
    wrapClick: (_isCustom) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const inputRef = vue.ref(null);
    const searchRef = vue.ref(null);
    const inputValue = vue.ref(
      props2.multiple || !props2.selectedLabel ? "" : props2.selectedLabel
    );
    const searchValue = vue.ref("");
    const isEmpty = vue.computed(() => {
      if (!props2.multiple) {
        return props2.value == null || props2.value === "";
      }
      return !Array.isArray(props2.value) || !props2.value.length;
    });
    const isFilterable = vue.computed(() => {
      if (props2.popperType && ["modal", "drawer", "default"].includes(props2.popperType)) {
        return false;
      }
      return props2.filterable;
    });
    const inputPlaceholder = vue.computed(() => {
      const str = isEmpty.value && props2.placeholder ? props2.placeholder : "";
      if (!isFilterable.value || !props2.visible || props2.multiple) {
        return str;
      }
      return props2.selectedLabel || str;
    });
    const isCollapse = vue.computed(() => {
      return typeof props2.maxTagCount === "number" && props2.selected != null && props2.selected.length > props2.maxTagCount;
    });
    const omittedSize = vue.computed(() => {
      if (isEmpty.value || props2.maxTagCount == null || props2.maxTagCount < 0) {
        return 0;
      }
      return props2.value.length - props2.maxTagCount;
    });
    const currentTags = vue.computed(() => {
      if (!isCollapse.value || isEmpty.value || props2.selected == null) {
        return props2.selected || [];
      }
      return props2.selected.slice(0, props2.maxTagCount);
    });
    const omittedTags = vue.computed(() => {
      if (!isCollapse.value || isEmpty.value || props2.selected == null) {
        return [];
      }
      return props2.selected.slice(props2.maxTagCount);
    });
    const focusSearchInput = () => {
      if (!isFilterable.value) {
        return;
      }
      const input = props2.multiple ? searchRef.value : inputRef.value;
      input && input.focus();
      vue.nextTick(() => {
        input && input.focus();
      });
    };
    const updateSearchValue = (modelValue) => {
      if (isFilterable.value && props2.visible && props2.multiple) {
        searchValue.value = modelValue;
        emit("filterChange", modelValue);
      }
    };
    const updateInputValue = (modelValue) => {
      if (isFilterable.value && props2.visible && !props2.multiple) {
        inputValue.value = modelValue;
        emit("filterChange", modelValue);
      }
    };
    const updateVisible = (visible) => {
      emit("update:visible", visible);
    };
    const handleTagClose = (item) => {
      if (!props2.disabled) {
        emit("removeTag", item);
      }
    };
    const handleClear = () => {
      emit("clear");
    };
    const handleInputClick = (e) => {
      emit("inputClick", e);
    };
    const handleInputFocus = (e) => {
      if (props2.automaticDropdown && !props2.visible) {
        updateVisible(true);
      }
      emit("focus", e);
    };
    const handleInputBlur = (e) => {
      emit("blur", e);
    };
    const handleInputEsc = (e) => {
      if (!props2.disabled && props2.visible) {
        e.stopPropagation();
        e.preventDefault();
        updateVisible(false);
      }
    };
    const handleWrapClick = (isCustom) => {
      emit("wrapClick", isCustom);
    };
    const openPopper = () => {
      updateVisible(true);
    };
    const closePopper = () => {
      updateVisible(false);
    };
    vue.watch(
      () => props2.selectedLabel,
      (label) => {
        if (!isFilterable.value || !props2.visible) {
          inputValue.value = props2.multiple || !label ? "" : label;
        }
      }
    );
    vue.watch(
      () => props2.visible,
      (visible) => {
        if (isFilterable.value) {
          if (props2.multiple) {
            searchValue.value = "";
            if (visible) {
              focusSearchInput();
            }
          } else {
            const label = props2.selectedLabel;
            inputValue.value = visible || !label ? "" : label;
          }
        }
      }
    );
    __expose({
      inputRef,
      searchRef,
      focusSearchInput,
      updateSearchValue,
      updateInputValue
    });
    return (_ctx, _cache) => {
      return _ctx.selectStyle === "none" ? vue.renderSlot(_ctx.$slots, "default", { key: 0 }) : _ctx.$slots.select ? (vue.openBlock(), vue.createElementBlock("div", {
        key: 1,
        class: vue.normalizeClass(_ctx.selectClass),
        style: vue.normalizeStyle(_ctx.selectStyle),
        onClick: _cache[0] || (_cache[0] = ($event) => handleWrapClick(true))
      }, [
        vue.renderSlot(_ctx.$slots, "select", {
          visible: _ctx.visible,
          value: _ctx.value,
          selectedLabel: _ctx.selectedLabel,
          selected: _ctx.selected,
          currentTags: currentTags.value,
          omittedTags: omittedTags.value,
          omittedSize: omittedSize.value,
          openPopper,
          closePopper,
          removeItem: handleTagClose,
          clear: handleClear
        }),
        vue.renderSlot(_ctx.$slots, "default")
      ], 6)) : (vue.openBlock(), vue.createElementBlock("div", {
        key: 2,
        class: vue.normalizeClass(["ele-select", [
          _ctx.selectClass,
          { "is-empty": isEmpty.value },
          { "is-multiple": _ctx.multiple },
          { "is-disabled": _ctx.disabled },
          { "is-filterable": isFilterable.value },
          { "is-small": _ctx.size === "small" },
          { "is-large": _ctx.size === "large" },
          { "is-opened": _ctx.visible }
        ]]),
        style: vue.normalizeStyle(_ctx.selectStyle),
        onClick: _cache[1] || (_cache[1] = ($event) => handleWrapClick(false))
      }, [
        vue.createVNode(vue.unref(elementPlus.ElInput), {
          ref_key: "inputRef",
          ref: inputRef,
          size: _ctx.size,
          disabled: _ctx.disabled,
          validateEvent: false,
          modelValue: inputValue.value,
          placeholder: isFilterable.value && _ctx.multiple && _ctx.visible ? "" : inputPlaceholder.value,
          readonly: !(isFilterable.value && !_ctx.multiple),
          style: vue.normalizeStyle(_ctx.inputStyle),
          "onUpdate:modelValue": updateInputValue,
          onClick: handleInputClick,
          onFocus: handleInputFocus,
          onBlur: handleInputBlur,
          onKeydown: vue.withKeys(handleInputEsc, ["esc"])
        }, vue.createSlots({
          suffix: vue.withCtx(() => [
            _ctx.clearable && !_ctx.disabled && !isEmpty.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElIcon), {
              key: 0,
              class: "ele-select-clear el-input__icon",
              onClick: vue.withModifiers(handleClear, ["stop"])
            }, {
              default: vue.withCtx(() => [
                vue.renderSlot(_ctx.$slots, "clearIcon", {}, () => [
                  vue.createVNode(vue.unref(index.CloseCircleFilled))
                ])
              ]),
              _: 3
            })) : vue.createCommentVNode("", true),
            vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-select-arrow el-input__icon" }, {
              default: vue.withCtx(() => [
                vue.renderSlot(_ctx.$slots, "suffixIcon", { visible: _ctx.visible }, () => [
                  vue.createVNode(vue.unref(index.ArrowDown))
                ])
              ]),
              _: 3
            })
          ]),
          _: 2
        }, [
          _ctx.$slots.prefix ? {
            name: "prefix",
            fn: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "prefix")
            ]),
            key: "0"
          } : void 0
        ]), 1032, ["size", "disabled", "modelValue", "placeholder", "readonly", "style"]),
        _ctx.multiple ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: "ele-select-tags",
          style: vue.normalizeStyle(_ctx.selectTagsStyle)
        }, [
          (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(currentTags.value, (item, index2) => {
            return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTag), {
              key: `${index2}-${item.value}`,
              size: _ctx.size,
              type: _ctx.tagType,
              closable: !_ctx.disabled,
              disableTransitions: true,
              title: item.label,
              onClose: ($event) => handleTagClose(item)
            }, {
              default: vue.withCtx(() => [
                item.label && _ctx.maxTagTextLength && item.label.length > _ctx.maxTagTextLength ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                  vue.createTextVNode(vue.toDisplayString(item.label.slice(0, _ctx.maxTagTextLength)) + "... ", 1)
                ], 64)) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                  vue.createTextVNode(vue.toDisplayString(item.label), 1)
                ], 64))
              ]),
              _: 2
            }, 1032, ["size", "type", "closable", "title", "onClose"]);
          }), 128)),
          isCollapse.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTag), {
            key: 0,
            size: _ctx.size,
            type: _ctx.tagType,
            disableTransitions: true
          }, {
            default: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "maxTagPlaceholder", {
                omittedValues: omittedTags.value,
                omittedSize: omittedSize.value
              }, () => [
                vue.createTextVNode(" +" + vue.toDisplayString(omittedSize.value), 1)
              ])
            ]),
            _: 3
          }, 8, ["size", "type"])) : vue.createCommentVNode("", true),
          !_ctx.disabled && isFilterable.value ? (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTag), {
            key: 1,
            size: _ctx.size,
            disableTransitions: true,
            class: "ele-select-search"
          }, {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElInput), {
                ref_key: "searchRef",
                ref: searchRef,
                size: _ctx.size,
                validateEvent: false,
                modelValue: searchValue.value,
                placeholder: inputPlaceholder.value,
                "onUpdate:modelValue": updateSearchValue,
                onKeydown: vue.withKeys(handleInputEsc, ["esc"])
              }, null, 8, ["size", "modelValue", "placeholder"])
            ]),
            _: 1
          }, 8, ["size"])) : vue.createCommentVNode("", true)
        ], 4)) : vue.createCommentVNode("", true),
        vue.renderSlot(_ctx.$slots, "default")
      ], 6));
    };
  }
});
module.exports = _sfc_main;
