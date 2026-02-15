"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const receiver = require("../ele-config-provider/receiver");
const common = require("../utils/common");
const renderCore = require("./components/render-core");
const renderUtil = require("./components/render-util");
const ProFormFooter = require("./components/pro-form-footer");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleProForm" },
  __name: "index",
  props: props.proFormProps,
  emits: props.proFormEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const footerSlotExcludes = [
      "default",
      "topExtra",
      "bottomExtra",
      "contentExtra"
    ];
    const slotExcludes = [...footerSlotExcludes, "footer", "footerExtra"];
    const props2 = __props;
    const emit = __emit;
    const formItems = vue.useModel(props2, "items");
    const { lang } = receiver.useLocale("proForm", props2);
    const config = vue.inject(receiver.injectContext, null);
    const formRef = vue.ref(null);
    const exposeMethods = {};
    [
      "validate",
      "validateField",
      "resetFields",
      "scrollToField",
      "clearValidate"
    ].forEach((key) => {
      exposeMethods[key] = (...params) => {
        if (!formRef.value) {
          throw new Error("formRef is null");
        }
        return formRef.value[key](...params);
      };
    });
    const childrenRef = vue.ref(null);
    const formSearchExpand = vue.ref(!!props2.searchExpand);
    const currentActiveKey = vue.ref(props2.activeItemKey);
    const footerStyleData = vue.computed(() => {
      return renderCore.translateJsCode(
        props2.footerStyle || {},
        props2.model || {},
        formItems.value || [],
        formSearchExpand.value,
        props2.httpRequest
      ).result;
    });
    const updateSearchExpand = (expand) => {
      formSearchExpand.value = expand;
      if (props2.searchExpand !== expand) {
        emit("update:searchExpand", expand);
      }
    };
    const updateValue = (prop, value) => {
      if (prop != null && config?.label && config?.size === 1) {
        emit("updateValue", prop, value);
      }
    };
    const handleUpdateItemsData = (items, parentItem) => {
      if (!parentItem) {
        formItems.value = items;
      } else {
        const parentItemKey = parentItem.key;
        common.eachTree(formItems.value, (item) => {
          if (item.key === parentItemKey) {
            item.children = items;
            return false;
          }
        });
      }
    };
    const handleUpdateActiveItemKey = (key) => {
      currentActiveKey.value = key;
      if (props2.activeItemKey !== key) {
        emit("update:activeItemKey", key);
      }
    };
    const handleSubmit = () => {
      if (formRef.value) {
        formRef.value.validate((valid) => {
          if (valid) {
            emit("submit", props2.model ?? {});
          }
        });
      }
    };
    const handleReset = () => {
      clearCodeCache();
      emit("reset");
      exposeMethods.clearValidate();
      vue.nextTick(() => {
        exposeMethods.clearValidate();
        vue.nextTick(() => {
          exposeMethods.clearValidate();
        });
      });
    };
    const handleFormSubmit = (e) => {
      if (props2.preventFormSubmit) {
        e.preventDefault();
      }
    };
    const handleFormValidate = (prop, isValid, message) => {
      emit("validate", prop, isValid, message);
    };
    vue.watch(
      () => props2.searchExpand,
      (expand) => {
        if (formSearchExpand.value !== expand) {
          formSearchExpand.value = expand;
        }
      }
    );
    vue.watch(
      () => props2.activeItemKey,
      (key) => {
        if (currentActiveKey.value !== key) {
          currentActiveKey.value = key;
        }
      }
    );
    const getProFormRefs = () => {
      return childrenRef.value?.$refs || {};
    };
    const codeCache = /* @__PURE__ */ new Map();
    const getAndCacheCode = (code, codeResult) => {
      const cacheResult = codeCache.get(code);
      if (cacheResult) {
        return cacheResult;
      }
      codeCache.set(code, codeResult);
      return codeResult;
    };
    const clearCodeCache = () => {
      codeCache.clear();
    };
    vue.onBeforeUnmount(() => {
      clearCodeCache();
    });
    __expose({
      ...exposeMethods,
      formRef,
      childrenRef,
      getProFormRefs,
      clearCodeCache
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElForm), {
        ref_key: "formRef",
        ref: formRef,
        model: _ctx.model,
        labelPosition: _ctx.labelPosition,
        labelWidth: _ctx.labelWidth,
        statusIcon: _ctx.statusIcon,
        validateOnRuleChange: _ctx.validateOnRuleChange,
        size: _ctx.size,
        disabled: _ctx.disabled,
        scrollToError: _ctx.scrollToError,
        scrollIntoViewOptions: _ctx.scrollIntoViewOptions,
        inline: _ctx.inline,
        labelSuffix: _ctx.labelSuffix,
        hideRequiredAsterisk: _ctx.hideRequiredAsterisk,
        requireAsteriskPosition: _ctx.requireAsteriskPosition,
        showMessage: _ctx.showMessage,
        inlineMessage: _ctx.inlineMessage,
        class: vue.normalizeClass(["ele-pro-form", { "is-editable": _ctx.editable }]),
        onValidate: handleFormValidate,
        onSubmit: handleFormSubmit
      }, {
        default: vue.withCtx(() => [
          vue.renderSlot(_ctx.$slots, "topExtra"),
          vue.createVNode(vue.unref(renderUtil.ChildrenRender), {
            ref_key: "childrenRef",
            ref: childrenRef,
            model: _ctx.model,
            items: vue.unref(formItems),
            rules: _ctx.rules,
            grid: _ctx.grid,
            rowProps: _ctx.rowProps,
            contentExtraColProps: _ctx.footerColProps,
            autoContentExtraCol: _ctx.autoFooterCol,
            formItems: vue.unref(formItems),
            searchExpand: formSearchExpand.value,
            editable: _ctx.editable,
            screenSize: _ctx.screenSize,
            activeItemKey: currentActiveKey.value,
            itemTypeData: _ctx.itemTypeData,
            httpRequest: _ctx.httpRequest,
            getProFormRefs,
            getAndCacheCode,
            requiredLang: vue.unref(lang).required,
            onUpdateItemValue: updateValue,
            onUpdateItemsData: handleUpdateItemsData,
            "onUpdate:activeItemKey": handleUpdateActiveItemKey
          }, vue.createSlots({ _: 2 }, [
            vue.renderList(Object.keys(_ctx.$slots).filter(
              (k) => !slotExcludes.includes(k)
            ), (name) => {
              return {
                name,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            }),
            _ctx.footer ? {
              name: "contentExtra",
              fn: vue.withCtx(() => [
                vue.createVNode(ProFormFooter, {
                  footerProps: _ctx.footerProps,
                  footerSlots: _ctx.footerSlots,
                  autoFooterCol: _ctx.autoFooterCol,
                  footerStyle: footerStyleData.value,
                  submitText: _ctx.submitText ?? vue.unref(lang).submit,
                  resetText: _ctx.resetText ?? vue.unref(lang).reset,
                  submitButtonProps: _ctx.submitButtonProps,
                  resetButtonProps: _ctx.resetButtonProps,
                  showSearchExpand: _ctx.showSearchExpand,
                  searchExpand: formSearchExpand.value,
                  searchExpandButtonProps: _ctx.searchExpandButtonProps,
                  searchExpandText: _ctx.searchExpandText ?? vue.unref(lang).expand,
                  searchShrinkText: _ctx.searchShrinkText ?? vue.unref(lang).shrink,
                  onSubmit: handleSubmit,
                  onReset: handleReset,
                  onUpdateSearchExpand: updateSearchExpand
                }, vue.createSlots({ _: 2 }, [
                  vue.renderList(Object.keys(_ctx.$slots).filter(
                    (k) => !footerSlotExcludes.includes(k)
                  ), (name) => {
                    return {
                      name,
                      fn: vue.withCtx((slotProps) => [
                        vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                      ])
                    };
                  })
                ]), 1032, ["footerProps", "footerSlots", "autoFooterCol", "footerStyle", "submitText", "resetText", "submitButtonProps", "resetButtonProps", "showSearchExpand", "searchExpand", "searchExpandButtonProps", "searchExpandText", "searchShrinkText"])
              ]),
              key: "0"
            } : void 0
          ]), 1032, ["model", "items", "rules", "grid", "rowProps", "contentExtraColProps", "autoContentExtraCol", "formItems", "searchExpand", "editable", "screenSize", "activeItemKey", "itemTypeData", "httpRequest", "requiredLang"]),
          vue.renderSlot(_ctx.$slots, "bottomExtra")
        ]),
        _: 3
      }, 8, ["model", "labelPosition", "labelWidth", "statusIcon", "validateOnRuleChange", "size", "disabled", "scrollToError", "scrollIntoViewOptions", "inline", "labelSuffix", "hideRequiredAsterisk", "requireAsteriskPosition", "showMessage", "inlineMessage", "class"]);
    };
  }
});
module.exports = _sfc_main;
