"use strict";
const vue = require("vue");
const common = require("../utils/common");
const util$1 = require("../ele-pro-layout/util");
const EleBasicSelect = require("../ele-basic-select/index");
const util = require("../ele-basic-select/util");
const EleButtons = require("../ele-buttons/index");
const EleProTable = require("../ele-pro-table/index");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTableSelect" },
  __name: "index",
  props: props.tableSelectProps,
  emits: props.tableSelectEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const ownSlots = ["popperTopExtra", "popperBottomExtra"];
    const props2 = __props;
    const emit = __emit;
    const { validateChange } = util.useFormValidate();
    const isResponsive = util$1.useResponsive(props2);
    const selectRef = vue.ref(null);
    const proTableRef = vue.ref(null);
    const selectVisible = vue.ref(false);
    const selectedItems = vue.ref([]);
    const tempSelectedItems = vue.ref([]);
    const tempSelectValue = vue.ref();
    const isModalType = vue.computed(() => {
      return props2.popperType === "modal" || props2.popperType === "drawer";
    });
    const selectPopperClass = vue.computed(() => {
      const classes = ["ele-table-select-popper"];
      if (isResponsive.value && !isModalType.value) {
        classes.push("is-responsive");
      }
      if (props2.popperClass) {
        classes.push(props2.popperClass);
      }
      return classes.join(" ");
    });
    const selectedLabel = vue.computed(() => {
      const selected = selectedItems.value;
      return !props2.multiple && selected.length ? selected[0].label : "";
    });
    const tableCurrentRowKey = vue.computed(() => {
      if (isModalType.value) {
        if (props2.multiple || util.isEmptyValue(tempSelectValue.value)) {
          return;
        }
        return tempSelectValue.value;
      }
      if (props2.multiple || util.isEmptyValue(props2.modelValue)) {
        return;
      }
      return props2.modelValue;
    });
    const tableSelectedRowKeys = vue.computed(() => {
      if (isModalType.value) {
        if (!props2.multiple || util.isEmptyValue(tempSelectValue.value)) {
          return;
        }
        return tempSelectValue.value;
      }
      if (!props2.multiple || util.isEmptyValue(props2.modelValue)) {
        return;
      }
      return props2.modelValue;
    });
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
      if (selectVisible.value !== visible) {
        selectVisible.value = visible;
        if (visible) {
          if (isModalType.value) {
            if (util.isEmptyValue(props2.modelValue)) {
              tempSelectedItems.value = [];
              tempSelectValue.value = void 0;
            } else {
              tempSelectedItems.value = [...selectedItems.value];
              tempSelectValue.value = props2.multiple ? [...props2.modelValue] : props2.modelValue;
            }
          }
          if (props2.tableProps?.virtual && proTableRef.value) {
            const virtualTableRef = proTableRef.value.getTableRef();
            if (virtualTableRef && !virtualTableRef.wrapWidth) {
              vue.nextTick(() => {
                virtualTableRef.updateWrapSize();
                vue.nextTick(() => {
                  updatePopover();
                });
              });
            }
          }
        }
        if (props2.visible !== visible) {
          emit("update:visible", visible);
        }
        emit("visibleChange", visible);
      }
    };
    const getChangedSelectedItems = (selectValue, selectedItems2, force) => {
      const tableData = [
        ...props2.cacheData || [],
        ...(props2.multiple ? props2.initValue : props2.initValue ? [props2.initValue] : void 0) || [],
        // 已废弃属性兼容
        ...(props2.multiple && proTableRef.value ? proTableRef.value.getSelectionRows() : void 0) || []
      ];
      if (!props2.multiple) {
        const temp = proTableRef.value ? proTableRef.value.getCurrentRow() : null;
        if (temp) {
          tableData.push(temp);
        }
      }
      if (!props2.multiple) {
        const value = selectValue;
        const d = selectedItems2.length ? selectedItems2[0] : null;
        if (util.isEmptyValue(value)) {
          if (d != null) {
            return [];
          }
          return;
        }
        if (force || !d || d.value !== value) {
          const item = tableData ? tableData.find((d2) => common.getValue(d2, props2.valueKey) === value) : void 0;
          let label = common.getValue(item, props2.labelKey);
          if (label == null && (!item || item._isMock)) {
            label = String(value);
          }
          return [{ value, label, data: item }];
        }
        return;
      }
      if (util.isEmptyValue(selectValue, true)) {
        if (selectedItems2.length) {
          return [];
        }
        return;
      }
      if (!force && !util.valueIsChanged(
        selectValue,
        selectedItems2.map((d) => d.value),
        true
      )) {
        return;
      }
      const selected = [];
      const dataKeys = tableData ? tableData.map((d) => common.getValue(d, props2.valueKey)) : [];
      selectValue.forEach((value, index) => {
        const dataIndex = dataKeys.indexOf(value);
        const item = dataIndex === -1 ? void 0 : tableData[dataIndex];
        let label = common.getValue(item, props2.labelKey);
        if (label == null && (!item || item._isMock)) {
          label = String(value);
        }
        selected.push({ value, label, index, data: item });
      });
      return selected;
    };
    const checkUpdateSelectedItems = (force) => {
      const items = getChangedSelectedItems(
        props2.modelValue,
        selectedItems.value,
        force
      );
      if (items) {
        selectedItems.value = items;
        vue.nextTick(() => {
          updatePopover();
        });
      }
    };
    const checkUpdateTempSelectedItems = (force) => {
      const items = getChangedSelectedItems(
        tempSelectValue.value,
        tempSelectedItems.value,
        force
      );
      if (items) {
        tempSelectedItems.value = items;
      }
    };
    const handleSelectRemove = (item) => {
      const values = props2.modelValue || [];
      updateModelValue(values.filter((v) => v !== item.value));
      emit("removeTag", item.value);
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
      emit("filterChange", keywords);
    };
    const handleUpdateModelValue = (modelValue) => {
      if (isModalType.value) {
        tempSelectValue.value = modelValue;
      } else {
        updateModelValue(modelValue);
      }
    };
    const handleCheckUpdateSelectedItems = (force) => {
      if (isModalType.value) {
        checkUpdateTempSelectedItems(force);
      } else {
        checkUpdateSelectedItems(force);
      }
    };
    const handleDataSelect = (data) => {
      if (!isModalType.value) {
        if (!props2.multiple) {
          updateVisible(false);
        }
        emit("select", data);
      }
    };
    const handleUpdateTableSelectedRowKeys = (rowKeys) => {
      if (props2.multiple) {
        const oldValues = props2.modelValue || [];
        const values = [...rowKeys];
        values.sort((a, b) => {
          const aOldIndex = oldValues.indexOf(a);
          const bOldIndex = oldValues.indexOf(b);
          const aIndex = aOldIndex === -1 ? values.length : aOldIndex;
          const bIndex = bOldIndex === -1 ? values.length : bOldIndex;
          return aIndex - bIndex;
        });
        handleUpdateModelValue(values);
      }
    };
    const handleUpdateTableCurrentRowKey = (rowKey) => {
      if (!props2.multiple) {
        handleUpdateModelValue(rowKey);
      }
    };
    const handleTableSelectionChange = () => {
      if (props2.multiple) {
        handleCheckUpdateSelectedItems(true);
      }
    };
    const handleTableCurrentChange = (row) => {
      if (!props2.multiple && row != null) {
        handleCheckUpdateSelectedItems(true);
      }
    };
    const handleTableRowClick = (row, _column, _e, disabled, selection) => {
      if (!props2.multiple) {
        handleDataSelect(row);
      } else if (props2.tableProps?.rowClickChecked && !disabled) {
        handleDataSelect(selection || []);
      }
    };
    const handleTableSelect = (selection) => {
      handleDataSelect(selection);
    };
    const handleTableSelectAll = (selection) => {
      handleDataSelect(selection);
    };
    const handleTableDone = () => {
      vue.nextTick(() => {
        updatePopover();
      });
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
    const handleInitValueChange = (initValue) => {
      if (!props2.multiple) {
        const value = common.getValue(initValue, props2.valueKey);
        if (value === props2.modelValue) {
          checkUpdateSelectedItems();
        } else {
          updateModelValue(value);
        }
        return;
      }
      const values = initValue.map(
        (d) => common.getValue(d, props2.valueKey)
      );
      if (!util.valueIsChanged(props2.modelValue, values, true)) {
        checkUpdateSelectedItems();
      } else {
        updateModelValue(values);
      }
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
      () => props2.cacheData,
      () => {
        checkUpdateSelectedItems(true);
        if (isModalType.value && selectVisible.value) {
          checkUpdateTempSelectedItems(true);
        }
      }
    );
    vue.watch(
      () => props2.modelValue,
      () => {
        checkUpdateSelectedItems();
      },
      { deep: true }
    );
    vue.watch(
      tempSelectValue,
      () => {
        if (isModalType.value && selectVisible.value) {
          checkUpdateTempSelectedItems();
        }
      },
      { deep: true }
    );
    vue.watch(
      () => props2.initValue,
      (initValue) => {
        if (!util.isEmptyValue(initValue)) {
          handleInitValueChange(initValue);
        }
      },
      { deep: true }
    );
    vue.onMounted(() => {
      if (!util.isEmptyValue(props2.initValue, props2.multiple)) {
        handleInitValueChange(props2.initValue);
      } else if (!util.isEmptyValue(props2.modelValue, props2.multiple)) {
        checkUpdateSelectedItems();
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
        const values = items.map((item) => item.value);
        updateModelValue(props2.multiple ? values : values[0]);
      },
      clearTempSelectedItems: () => {
        tempSelectedItems.value = [];
        tempSelectValue.value = null;
      },
      removeTempSelectedItem: (item) => {
        const index = tempSelectedItems.value.indexOf(item);
        tempSelectedItems.value.splice(index, 1);
        const values = tempSelectedItems.value.map((item2) => item2.value);
        tempSelectValue.value = props2.multiple ? values : values[0];
      },
      updateTempSelectedItems: (items) => {
        tempSelectedItems.value = items;
        const values = tempSelectedItems.value.map((item) => item.value);
        tempSelectValue.value = props2.multiple ? values : values[0];
      }
    };
    vue.provide(util.SELECT_DATA_KEY, {
      selectedItems,
      tempSelectedItems,
      ...provideMethods
    });
    __expose({
      selectRef,
      tableRef: proTableRef,
      updatePopover,
      updateVisible,
      focusSearchInput,
      ...provideMethods
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleBasicSelect, {
        ref_key: "selectRef",
        ref: selectRef,
        value: _ctx.modelValue,
        selectedLabel: selectedLabel.value,
        selected: selectedItems.value,
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
              vue.renderSlot(_ctx.$slots, "popperTopExtra"),
              vue.createVNode(EleProTable, vue.mergeProps({
                "onUpdate:selectedRowKeys": handleUpdateTableSelectedRowKeys,
                "onUpdate:currentRowKey": handleUpdateTableCurrentRowKey,
                onSelectionChange: handleTableSelectionChange,
                onCurrentChange: handleTableCurrentChange,
                onRowClick: handleTableRowClick,
                onSelect: handleTableSelect,
                onSelectAll: handleTableSelectAll,
                onDone: handleTableDone
              }, _ctx.tableProps || {}, {
                ref_key: "proTableRef",
                ref: proTableRef,
                rowKey: _ctx.valueKey,
                reserveCurrent: true,
                highlightCurrentRow: !_ctx.multiple,
                currentRowKey: tableCurrentRowKey.value,
                selectedRowKeys: tableSelectedRowKeys.value
              }), vue.createSlots({ _: 2 }, [
                vue.renderList(vue.unref(common.getSlotsMap)(
                  _ctx.$slots,
                  _ctx.tableSlots,
                  [],
                  ownSlots,
                  !_ctx.tableSlots
                ), (slotName, compSlotName) => {
                  return {
                    name: compSlotName,
                    fn: vue.withCtx((slotProps) => [
                      vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                    ])
                  };
                })
              ]), 1040, ["rowKey", "highlightCurrentRow", "currentRowKey", "selectedRowKeys"]),
              vue.renderSlot(_ctx.$slots, "popperBottomExtra")
            ]),
            _: 3
          }, 16)) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
            vue.renderSlot(_ctx.$slots, "popperTopExtra"),
            vue.createVNode(EleProTable, vue.mergeProps({
              "onUpdate:selectedRowKeys": handleUpdateTableSelectedRowKeys,
              "onUpdate:currentRowKey": handleUpdateTableCurrentRowKey,
              onSelectionChange: handleTableSelectionChange,
              onCurrentChange: handleTableCurrentChange,
              onRowClick: handleTableRowClick,
              onSelect: handleTableSelect,
              onSelectAll: handleTableSelectAll,
              onDone: handleTableDone
            }, _ctx.tableProps || {}, {
              ref_key: "proTableRef",
              ref: proTableRef,
              rowKey: _ctx.valueKey,
              reserveCurrent: true,
              highlightCurrentRow: !_ctx.multiple,
              currentRowKey: tableCurrentRowKey.value,
              selectedRowKeys: tableSelectedRowKeys.value
            }), vue.createSlots({ _: 2 }, [
              vue.renderList(vue.unref(common.getSlotsMap)(
                _ctx.$slots,
                _ctx.tableSlots,
                [],
                ownSlots,
                !_ctx.tableSlots
              ), (slotName, compSlotName) => {
                return {
                  name: compSlotName,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1040, ["rowKey", "highlightCurrentRow", "currentRowKey", "selectedRowKeys"]),
            vue.renderSlot(_ctx.$slots, "popperBottomExtra")
          ], 64))
        ]),
        _: 2
      }, [
        vue.renderList(Object.keys(_ctx.$slots).filter(
          (k) => k !== "default" && !ownSlots.includes(k)
        ), (name) => {
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
