"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../utils/common");
const hook = require("../utils/hook");
const util = require("../ele-basic-select/util");
const EleBasicSelect = require("../ele-basic-select/index");
const EleButtons = require("../ele-buttons/index");
const props = require("./props");
const _hoisted_1 = ["title"];
const _hoisted_2 = ["title"];
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTreeSelect" },
  __name: "index",
  props: props.treeSelectProps,
  emits: props.treeSelectEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const ownSlots = ["default", "empty"];
    const props2 = __props;
    const emit = __emit;
    const { validateChange } = util.useFormValidate();
    const { optionData, reloadOptions } = hook.useProOptions(props2, "treeProps.data");
    const selectRef = vue.ref(null);
    const treeRef = vue.ref(null);
    const selectVisible = vue.ref(!props2.disabled && props2.visible);
    const selectedItems = vue.ref([]);
    const tempSelectedItems = vue.ref([]);
    const tempSelectValue = vue.ref();
    const isModalType = vue.computed(() => {
      return props2.popperType === "modal" || props2.popperType === "drawer";
    });
    const selectPopperClass = vue.computed(() => {
      const classes = ["ele-tree-select-popper"];
      if (props2.popperClass) {
        classes.push(props2.popperClass);
      }
      return classes.join(" ");
    });
    const selectedLabel = vue.computed(() => {
      const selected = selectedItems.value;
      return !props2.multiple && selected.length ? selected[0].label : "";
    });
    const treeOptions = vue.computed(() => {
      return Object.assign(
        {
          value: "id",
          label: "label",
          children: "children",
          disabled: "disabled"
        },
        props2.treeProps?.props
      );
    });
    const updateTreeChecked = (value) => {
      if (treeRef.value) {
        if (props2.multiple) {
          if (util.isEmptyValue(value, true)) {
            treeRef.value.setCheckedKeys([]);
          } else {
            treeRef.value.setCheckedKeys(value);
          }
        } else {
          if (util.isEmptyValue(value)) {
            treeRef.value.setCurrentKey(null);
          } else {
            treeRef.value.setCurrentKey(value);
          }
        }
      }
    };
    const updatePopover = () => {
      selectRef.value && selectRef.value.updatePopper();
    };
    const focusSearchInput = () => {
      selectRef.value && selectRef.value.focusSearchInput();
    };
    const updateModelValue = (modelValue) => {
      if (util.valueIsChanged(modelValue, props2.modelValue, props2.multiple)) {
        emit("update:modelValue", modelValue);
        if (props2.validateEvent) {
          validateChange();
        }
        emit("change", modelValue);
      }
    };
    const updateVisible = (visible) => {
      if (visible) {
        handleSelectFilter("");
      }
      if (selectVisible.value !== visible) {
        selectVisible.value = visible;
        if (visible && isModalType.value) {
          if (util.isEmptyValue(props2.modelValue)) {
            tempSelectedItems.value = [];
            tempSelectValue.value = void 0;
          } else {
            tempSelectedItems.value = [...selectedItems.value];
            tempSelectValue.value = props2.multiple ? [...props2.modelValue] : props2.modelValue;
          }
          if (!treeRef.value) {
            vue.nextTick(() => {
              updateTreeChecked(tempSelectValue.value);
            });
          }
        }
        if (props2.visible !== visible) {
          emit("update:visible", visible);
        }
        emit("visibleChange", visible);
      }
    };
    const nodeIsCheckAll = (child, values) => {
      if (!child || !child.length || !values || !values.length) {
        return false;
      }
      const valueKey = treeOptions.value.value;
      const childKey = treeOptions.value.children;
      const disabledKey = treeOptions.value.disabled;
      return child.every((d) => {
        if (common.getValue(d, disabledKey) || values.includes(common.getValue(d, valueKey))) {
          return true;
        }
        const cChild = common.getValue(d, childKey);
        if (cChild && cChild.length) {
          return nodeIsCheckAll(cChild, values);
        }
        return false;
      });
    };
    const nodeIsCheckAllSimple = (child, items) => {
      const valueKey = treeOptions.value.value;
      const disabledKey = treeOptions.value.disabled;
      const values = items.map((item) => item.value);
      return child.every((d) => {
        if (common.getValue(d, disabledKey) || values.includes(common.getValue(d, valueKey))) {
          return true;
        }
        return false;
      });
    };
    const getSelectedItemsPro = (values, data, leaf, hide, parentChecked) => {
      const items = [];
      if (!data) {
        return items;
      }
      const valueKey = treeOptions.value.value;
      const labelKey = treeOptions.value.label;
      const childKey = treeOptions.value.children;
      data.forEach((d) => {
        const value = common.getValue(d, valueKey);
        const child = common.getValue(d, childKey);
        const checked = values.includes(value);
        if (leaf) {
          const hasChild = !!(child && child.length);
          const cItems = hasChild ? getSelectedItemsPro(values, child, leaf) : [];
          if (checked || hasChild && nodeIsCheckAllSimple(child, cItems)) {
            const label = common.getValue(d, labelKey);
            items.push({ value, label, hide: hasChild, data: d });
          }
          cItems.forEach((t) => {
            items.push(t);
          });
          return;
        }
        if (checked || parentChecked) {
          const label = common.getValue(d, labelKey);
          items.push({ value, label, hide, data: d });
        }
        const cHide = checked || hide;
        getSelectedItemsPro(values, child, leaf, cHide, checked).forEach((t) => {
          items.push(t);
        });
      });
      return items;
    };
    const getSelectedItems = (checkedKeys) => {
      if (util.isEmptyValue(checkedKeys, true)) {
        return [];
      }
      const values = checkedKeys;
      const valueKey = treeOptions.value.value;
      const labelKey = treeOptions.value.label;
      const childKey = treeOptions.value.children;
      const cacheData = props2.cacheData;
      const scs = props2.showCheckedStrategy;
      if (props2.multiple && !(props2.treeProps?.checkStrictly || scs === "all")) {
        const leaf = scs === "child";
        const items2 = getSelectedItemsPro(values, optionData.value, leaf);
        const selectedValues = items2.map((t) => t.value);
        const ids2 = (cacheData || []).map((d) => common.getValue(d, valueKey));
        values.forEach((value) => {
          if (!selectedValues.includes(value)) {
            const i = ids2.indexOf(value);
            const d = cacheData && i !== -1 ? cacheData[i] : void 0;
            const label = d ? common.getValue(d, labelKey) : String(value);
            items2.push({ value, label, data: d });
          }
        });
        items2.sort((a, b) => {
          const aOldIndex = values.indexOf(a.value);
          const bOldIndex = values.indexOf(b.value);
          const aIndex = aOldIndex === -1 ? items2.length : aOldIndex;
          const bIndex = bOldIndex === -1 ? items2.length : bOldIndex;
          return aIndex - bIndex;
        });
        return items2;
      }
      const ids = [];
      const data = [];
      if (cacheData) {
        cacheData.forEach((d) => {
          const value = common.getValue(d, valueKey);
          ids.push(value);
          data.push(d);
        });
      }
      common.eachTree(
        optionData.value,
        (d) => {
          ids.push(common.getValue(d, valueKey));
          data.push(d);
        },
        childKey
      );
      const items = [];
      values.forEach((value) => {
        const i = ids.indexOf(value);
        const d = i === -1 ? void 0 : data[i];
        const label = d ? common.getValue(d, labelKey) : String(value);
        items.push({ value, label, data: d });
      });
      return items;
    };
    const getSelectedValues = (checkedKeys, items) => {
      if (!props2.multiple) {
        return checkedKeys ? checkedKeys[0] : void 0;
      }
      if (!props2.checkedValueStrategy) {
        return checkedKeys || [];
      }
      const values = [];
      items.forEach((d) => {
        if (!d.hide) {
          values.push(d.value);
        }
      });
      return values;
    };
    const updateSelectedItems = (value, t) => {
      if (t) {
        selectedItems.value = t;
      } else if (util.isEmptyValue(value, props2.multiple)) {
        selectedItems.value = [];
      } else {
        const items = getSelectedItems(props2.multiple ? value : [value]);
        selectedItems.value = items;
      }
      vue.nextTick(() => {
        updatePopover();
      });
    };
    const updateTempSelectedItems = (value, t) => {
      if (t) {
        tempSelectedItems.value = t;
      } else if (util.isEmptyValue(value, props2.multiple)) {
        tempSelectedItems.value = [];
      } else {
        const items = getSelectedItems(props2.multiple ? value : [value]);
        tempSelectedItems.value = items;
      }
    };
    const updateSelectedItemsAndValue = (checkedKeys, itemsData, modalType) => {
      const items = itemsData || getSelectedItems(checkedKeys);
      const values = getSelectedValues(checkedKeys, items);
      if (modalType ?? isModalType.value) {
        updateTempSelectedItems(void 0, items);
        tempSelectValue.value = values;
      } else {
        updateSelectedItems(void 0, items);
        updateModelValue(values);
      }
    };
    const getSortedCheckedKeys = (modalType) => {
      const oldValues = (modalType ?? isModalType.value ? tempSelectedItems.value : selectedItems.value).map((item) => item.value);
      const checkedKeys = treeRef.value ? treeRef.value.getCheckedKeys() : null;
      const keys = [...checkedKeys || []];
      keys.sort((a, b) => {
        const aOldIndex = oldValues.indexOf(a);
        const bOldIndex = oldValues.indexOf(b);
        const aIndex = aOldIndex === -1 ? keys.length : aOldIndex;
        const bIndex = bOldIndex === -1 ? keys.length : bOldIndex;
        return aIndex - bIndex;
      });
      return keys;
    };
    const handleSelectRemove = (item) => {
      if (treeRef.value && !(isModalType.value && selectVisible.value)) {
        treeRef.value.setChecked(item.value, false);
        const keys = getSortedCheckedKeys(false);
        updateSelectedItemsAndValue(keys, null, false);
        emit("removeTag", item.value);
      }
    };
    const handleSelectClear = () => {
      updateModelValue(props2.multiple ? [] : null);
      updateVisible(false);
      emit("clear");
    };
    const handleSelectFocus = (e) => {
      emit("focus", e);
    };
    const handleSelectBlur = (e) => {
      emit("blur", e);
    };
    const handleSelectFilter = (keywords) => {
      treeRef.value && treeRef.value.filter(keywords);
    };
    const treeFilter = (keywords, item) => {
      const label = common.getValue(item, treeOptions.value.label);
      return label != null && label.includes(keywords);
    };
    const handleTreeClick = (item, _node, e) => {
      e.stopPropagation();
      const valueKey = treeOptions.value.value;
      const childrenKey = treeOptions.value.children;
      const disabledKey = treeOptions.value.disabled;
      const disabled = common.getValue(item, disabledKey);
      if (disabled) {
        const target = e.target;
        if (target && target.classList.contains("is-disabled")) {
          const el = target.parentNode?.parentNode;
          el && el.blur();
        }
      }
      focusSearchInput();
      const value = common.getValue(item, valueKey);
      const isChild = !common.getValue(item, childrenKey)?.length;
      const expandOnClick = props2.treeProps?.expandOnClickNode !== false;
      if (!props2.multiple) {
        const selectedItem = selectedItems.value[0];
        if (selectedItem && selectedItem.value === value) {
          if ((!expandOnClick || isChild) && !isModalType.value) {
            updateVisible(false);
          }
          return;
        }
        if (!disabled && (!expandOnClick || isChild)) {
          const label = common.getValue(item, treeOptions.value.label);
          updateSelectedItemsAndValue([value], [{ label, value, data: item }]);
          if (!isModalType.value) {
            updateVisible(false);
          }
          return;
        }
        vue.nextTick(() => {
          const id = isModalType.value ? tempSelectValue.value : props2.modelValue;
          const key = util.isEmptyValue(id) ? null : id;
          treeRef.value && treeRef.value.setCurrentKey(key);
        });
        return;
      }
      if (!disabled && (!expandOnClick || isChild) && !isChild && treeRef.value) {
        const values = treeRef.value.getCheckedKeys() || [];
        const checked = values.includes(value);
        if (checked) {
          treeRef.value.setChecked(value, false);
        } else if (isChild) {
          treeRef.value.setChecked(value, !checked);
        } else {
          const child = common.getValue(item, childrenKey);
          const isCheckAll = nodeIsCheckAll(child, values);
          treeRef.value.setChecked(value, !isCheckAll);
        }
        updateSelectedItemsAndValue(getSortedCheckedKeys());
      }
    };
    const handleTreeCheck = () => {
      updateSelectedItemsAndValue(getSortedCheckedKeys());
      focusSearchInput();
    };
    const handleTreeExpand = () => {
      focusSearchInput();
    };
    const handleTreeCollapse = () => {
      focusSearchInput();
    };
    const handleConfirm = () => {
      const selected = tempSelectedItems.value.map((item) => item.data);
      const selectedData = props2.multiple ? selected : selected[0];
      if (props2.beforeConfirm && props2.beforeConfirm(selectedData) === false) {
        return;
      }
      const values = tempSelectedItems.value.map((item) => item.value);
      if (!props2.multiple) {
        updateModelValue(values[0]);
        emit("select", selectedData);
        updateVisible(false);
        return;
      }
      updateModelValue(values);
      emit("select", selectedData);
      updateVisible(false);
    };
    vue.watch(
      () => props2.disabled,
      (disabled) => {
        if (disabled) {
          updateVisible(false);
        }
      }
    );
    vue.watch(
      () => props2.visible,
      (visible) => {
        updateVisible(visible);
      }
    );
    vue.watch(
      optionData,
      () => {
        vue.nextTick(() => {
          updateTreeChecked(props2.modelValue);
        });
      },
      { deep: true }
    );
    vue.watch(
      [() => props2.cacheData, optionData],
      () => {
        const value = props2.multiple ? selectedItems.value.map((item) => item.value) : props2.modelValue;
        updateSelectedItems(value);
        if (isModalType.value && selectVisible.value) {
          const value2 = props2.multiple ? tempSelectedItems.value.map((item) => item.value) : tempSelectValue.value;
          updateTempSelectedItems(value2);
        }
      },
      { deep: true }
    );
    vue.watch(
      () => props2.modelValue,
      (value) => {
        updateSelectedItems(value);
        if (!(isModalType.value && selectVisible.value)) {
          updateTreeChecked(value);
        }
      },
      { deep: true }
    );
    vue.watch(
      tempSelectValue,
      (value) => {
        if (isModalType.value && selectVisible.value) {
          updateTempSelectedItems(value);
          updateTreeChecked(value);
        }
      },
      { deep: true }
    );
    vue.watch(
      [() => props2.showCheckedStrategy, () => props2.treeProps?.checkStrictly],
      () => {
        if (props2.multiple) {
          if (util.isEmptyValue(props2.modelValue, true)) {
            updateSelectedItems(void 0, []);
          } else {
            const keys = selectedItems.value.map((item) => item.value);
            updateSelectedItemsAndValue(keys, null, false);
          }
          if (isModalType.value && selectVisible.value) {
            if (util.isEmptyValue(tempSelectValue.value, true)) {
              updateTempSelectedItems(void 0, []);
            } else {
              const keys = tempSelectedItems.value.map((item) => item.value);
              updateSelectedItemsAndValue(keys, null, true);
            }
          }
        }
      }
    );
    vue.watch(
      () => props2.checkedValueStrategy,
      () => {
        if (props2.multiple) {
          if (!util.isEmptyValue(props2.modelValue, true)) {
            const keys = selectedItems.value.map((item) => item.value);
            updateModelValue(getSelectedValues(keys, selectedItems.value));
          }
          if (isModalType.value && selectVisible.value && !util.isEmptyValue(tempSelectValue.value, true)) {
            const k = tempSelectedItems.value.map((item) => item.value);
            tempSelectValue.value = getSelectedValues(k, tempSelectedItems.value);
          }
        }
      }
    );
    vue.onMounted(() => {
      if (!util.isEmptyValue(props2.modelValue, props2.multiple)) {
        updateSelectedItems(props2.modelValue);
        if (isModalType.value && selectVisible.value) {
          tempSelectedItems.value = [...selectedItems.value];
          tempSelectValue.value = props2.multiple ? [...props2.modelValue] : props2.modelValue;
        }
        updateTreeChecked(props2.modelValue);
      }
    });
    const provideMethods = {
      clearSelectedItems: handleSelectClear,
      removeSelectedItem: (item) => {
        if (props2.multiple) {
          handleSelectRemove(item);
        } else if (props2.modelValue === item.value) {
          handleSelectClear();
        }
      },
      updateSelectedItems: (items) => {
        const keys = items.map((item) => item.value);
        updateSelectedItemsAndValue(keys, items, false);
      },
      clearTempSelectedItems: () => {
        tempSelectedItems.value = [];
        tempSelectValue.value = null;
      },
      removeTempSelectedItem: (item) => {
        if (props2.multiple) {
          if (treeRef.value && isModalType.value && selectVisible.value) {
            treeRef.value.setChecked(item.value, false);
            const keys = getSortedCheckedKeys(true);
            updateSelectedItemsAndValue(keys, null, true);
          }
        } else if (tempSelectValue.value === item.value) {
          tempSelectedItems.value = [];
          tempSelectValue.value = null;
        }
      },
      updateTempSelectedItems: (items) => {
        const keys = items.map((item) => item.value);
        updateSelectedItemsAndValue(keys, items, true);
      }
    };
    vue.provide(util.SELECT_DATA_KEY, {
      selectedItems,
      tempSelectedItems,
      ...provideMethods
    });
    __expose({
      selectRef,
      treeRef,
      updatePopover,
      updateVisible,
      focusSearchInput,
      reloadOptions,
      ...provideMethods,
      selectedItems,
      selectedLabel
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleBasicSelect, {
        ref_key: "selectRef",
        ref: selectRef,
        value: _ctx.modelValue,
        selectedLabel: selectedLabel.value,
        selected: selectedItems.value.filter((d) => !d.hide),
        visible: selectVisible.value,
        multiple: _ctx.multiple,
        disabled: _ctx.disabled,
        size: _ctx.size,
        clearable: _ctx.clearable,
        placeholder: _ctx.placeholder,
        maxTagCount: _ctx.maxTagCount,
        maxTagTextLength: _ctx.maxTagTextLength,
        tagType: _ctx.tagType,
        automaticDropdown: _ctx.automaticDropdown,
        filterable: _ctx.filterable,
        selectClass: _ctx.selectClass,
        selectStyle: _ctx.selectStyle,
        inputStyle: _ctx.inputStyle,
        selectTagsStyle: _ctx.selectTagsStyle,
        popperClass: selectPopperClass.value,
        popperWidth: _ctx.popperWidth,
        popperHeight: _ctx.popperHeight,
        popperType: _ctx.popperType,
        popperProps: _ctx.popperProps,
        popperSlots: { footer: "modalFooter", ..._ctx.popperSlots || {} },
        popperTitle: _ctx.popperTitle,
        teleported: _ctx.teleported,
        persistent: _ctx.persistent,
        placement: _ctx.placement,
        transition: _ctx.transition,
        popperOptions: _ctx.popperOptions,
        "onUpdate:visible": updateVisible,
        onFilterChange: handleSelectFilter,
        onRemoveTag: handleSelectRemove,
        onClear: handleSelectClear,
        onFocus: handleSelectFocus,
        onBlur: handleSelectBlur
      }, vue.createSlots({
        default: vue.withCtx(() => [
          _ctx.wrapperComponent ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.wrapperComponent), vue.normalizeProps(vue.mergeProps({ key: 0 }, _ctx.wrapperComponentProps || {})), {
            default: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElTreeV2), vue.mergeProps({
                itemSize: 32,
                filterMethod: treeFilter
              }, vue.unref(common.omit)(_ctx.treeProps, ["data"]), {
                ref_key: "treeRef",
                ref: treeRef,
                data: vue.unref(optionData),
                props: treeOptions.value,
                highlightCurrent: _ctx.multiple ? false : true,
                showCheckbox: !!_ctx.multiple,
                checkOnClickNode: false,
                onCheck: handleTreeCheck,
                onNodeClick: handleTreeClick,
                onNodeExpand: handleTreeExpand,
                onNodeCollapse: handleTreeCollapse
              }), vue.createSlots({
                default: vue.withCtx((slotProps) => [
                  vue.createElementVNode("span", {
                    class: vue.normalizeClass(["el-tree-node__label", { "is-disabled": slotProps.node.disabled }]),
                    title: slotProps.node.label
                  }, [
                    vue.renderSlot(_ctx.$slots, "default", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})), () => [
                      vue.createTextVNode(vue.toDisplayString(slotProps.node.label), 1)
                    ])
                  ], 10, _hoisted_1)
                ]),
                _: 2
              }, [
                _ctx.$slots.empty ? {
                  name: "empty",
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, "empty", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ]),
                  key: "0"
                } : void 0
              ]), 1040, ["data", "props", "highlightCurrent", "showCheckbox"])
            ]),
            _: 3
          }, 16)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElTreeV2), vue.mergeProps({
            key: 1,
            itemSize: 32,
            filterMethod: treeFilter
          }, vue.unref(common.omit)(_ctx.treeProps, ["data"]), {
            ref_key: "treeRef",
            ref: treeRef,
            data: vue.unref(optionData),
            props: treeOptions.value,
            highlightCurrent: _ctx.multiple ? false : true,
            showCheckbox: !!_ctx.multiple,
            checkOnClickNode: false,
            onCheck: handleTreeCheck,
            onNodeClick: handleTreeClick,
            onNodeExpand: handleTreeExpand,
            onNodeCollapse: handleTreeCollapse
          }), vue.createSlots({
            default: vue.withCtx((slotProps) => [
              vue.createElementVNode("span", {
                class: vue.normalizeClass(["el-tree-node__label", { "is-disabled": slotProps.node.disabled }]),
                title: slotProps.node.label
              }, [
                vue.renderSlot(_ctx.$slots, "default", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})), () => [
                  vue.createTextVNode(vue.toDisplayString(slotProps.node.label), 1)
                ])
              ], 10, _hoisted_2)
            ]),
            _: 2
          }, [
            _ctx.$slots.empty ? {
              name: "empty",
              fn: vue.withCtx((slotProps) => [
                vue.renderSlot(_ctx.$slots, "empty", vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
              ]),
              key: "0"
            } : void 0
          ]), 1040, ["data", "props", "highlightCurrent", "showCheckbox"]))
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
        isModalType.value && !_ctx.$slots.modalFooter ? {
          name: "modalFooter",
          fn: vue.withCtx(() => [
            vue.createVNode(EleButtons, {
              items: [
                { preset: "cancel", onClick: () => updateVisible(false) },
                { preset: "confirm", onClick: () => handleConfirm() }
              ]
            }, null, 8, ["items"])
          ]),
          key: "0"
        } : void 0
      ]), 1032, ["value", "selectedLabel", "selected", "visible", "multiple", "disabled", "size", "clearable", "placeholder", "maxTagCount", "maxTagTextLength", "tagType", "automaticDropdown", "filterable", "selectClass", "selectStyle", "inputStyle", "selectTagsStyle", "popperClass", "popperWidth", "popperHeight", "popperType", "popperProps", "popperSlots", "popperTitle", "teleported", "persistent", "placement", "transition", "popperOptions"]);
    };
  }
});
module.exports = _sfc_main;
