"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const VueDraggable = require("vuedraggable");
const renderCore = require("./render-core");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "DraggableRow" },
  __name: "draggable-row",
  props: {
    itemsData: {},
    componentData: {},
    screenSize: {},
    gridColProps: {},
    formData: {},
    formItems: {},
    searchExpand: { type: Boolean },
    httpRequest: {},
    getProFormRefs: { type: Function },
    getAndCacheCode: { type: Function },
    autoContentExtraCol: { type: Boolean },
    contentExtraColProps: {},
    editable: { type: Boolean }
  },
  emits: ["updateItems"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const handleUpdateItemsModelValue = (data) => {
      emit("updateItems", data);
    };
    const ns = elementPlus.useNamespace("row");
    const gutter = vue.computed(() => props.componentData?.gutter ?? 0);
    const rowStyle = vue.computed(() => {
      const styles = {};
      if (!props.componentData?.gutter) {
        return styles;
      }
      styles.marginRight = styles.marginLeft = `-${props.componentData.gutter / 2}px`;
      return styles;
    });
    const rowClass = vue.computed(() => [
      "ele-pro-form-builder-grid-container-wrapper",
      ns.b(),
      ns.is(
        `justify-${props.componentData?.justify ?? "start"}`,
        (props.componentData?.justify ?? "start") !== "start"
      ),
      ns.is(`align-${props.componentData?.align}`, !!props.componentData?.align)
    ]);
    vue.provide(elementPlus.rowContextKey, { gutter });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(VueDraggable), {
        itemKey: "key",
        animation: 150,
        modelValue: __props.itemsData,
        setData: () => void 0,
        group: vue.unref(renderCore.sortableGroupName),
        handle: ".ele-pro-form-builder-item-handle",
        draggable: ".ele-pro-form-builder-grid-item-wrapper",
        tag: __props.componentData?.tag ?? "div",
        class: vue.normalizeClass(rowClass.value),
        style: vue.normalizeStyle(rowStyle.value),
        "onUpdate:modelValue": handleUpdateItemsModelValue
      }, vue.createSlots({
        item: vue.withCtx(({ element }) => [
          (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElCol), vue.mergeProps(
            {
              key: element.key ?? element.prop,
              class: "ele-pro-form-builder-grid-item-wrapper"
            },
            vue.unref(renderCore.getScreenSizeColProps)(
              __props.screenSize,
              __props.gridColProps,
              vue.unref(renderCore.translateJsCode)(
                element.colProps || {},
                __props.formData,
                __props.formItems || [],
                __props.searchExpand,
                __props.httpRequest,
                __props.getProFormRefs,
                __props.getAndCacheCode
              ).result
            )
          ), {
            default: vue.withCtx(() => [
              vue.renderSlot(_ctx.$slots, "item", { element })
            ]),
            _: 2
          }, 1040))
        ]),
        _: 2
      }, [
        _ctx.$slots.footer ? {
          name: "footer",
          fn: vue.withCtx(() => [
            vue.createVNode(vue.unref(elementPlus.ElCol), vue.normalizeProps(vue.guardReactiveProps(
              vue.unref(renderCore.getScreenSizeColProps)(
                __props.screenSize,
                __props.autoContentExtraCol ? vue.unref(renderCore.computeContentExtraCol)(
                  __props.gridColProps,
                  (__props.formItems || []).filter(
                    (item) => vue.unref(renderCore.isShowItem)(
                      item,
                      __props.formData,
                      __props.formItems || [],
                      __props.searchExpand,
                      __props.editable
                    )
                  ).length
                ) : { span: 24 },
                vue.unref(renderCore.translateJsCode)(
                  __props.contentExtraColProps || {},
                  __props.formData,
                  __props.formItems || [],
                  __props.searchExpand,
                  __props.httpRequest,
                  __props.getProFormRefs,
                  __props.getAndCacheCode
                ).result
              )
            )), {
              default: vue.withCtx(() => [
                vue.renderSlot(_ctx.$slots, "footer")
              ]),
              _: 3
            }, 16)
          ]),
          key: "0"
        } : void 0
      ]), 1032, ["modelValue", "group", "tag", "class", "style"]);
    };
  }
});
module.exports = _sfc_main;
