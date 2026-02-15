"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const common = require("../../utils/common");
const EleLoading = require("../../ele-loading/index");
const util = require("../util");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "PageSide" },
  __name: "page-side",
  props: {
    /** 侧栏配置 */
    sideConfig: Object,
    /** 数据 */
    data: Array,
    /** 加载状态 */
    loading: Boolean,
    /** 加载错误信息 */
    errorMessage: String,
    /** 选中值 */
    selectedValue: [String, Number, Boolean, Object, Array],
    /** 侧栏树搜索关键字 */
    keywords: String,
    /** 国际化 */
    lang: {
      type: Object,
      required: true
    }
  },
  emits: {
    /** 侧栏树点击事件 */
    treeNodeClick: (_nodeValue) => true
  },
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const treeRef = vue.ref(null);
    const setTreeCurrentKey = (key) => {
      if (key != null) {
        try {
          treeRef.value?.setCurrentKey?.(key);
        } catch (e) {
          console.error(e);
        }
      }
    };
    const handleNodeClick = (item) => {
      if (item != null) {
        emit("treeNodeClick", item[util.getTreeValueField(props.sideConfig)]);
      }
    };
    const filterNode = (value, item) => {
      if (value) {
        const itemLabel = item[util.getTreeLabelField(props.sideConfig)];
        return !!(itemLabel && itemLabel.includes(value));
      }
      return true;
    };
    vue.watch(
      () => props.keywords,
      (value) => {
        treeRef.value?.filter?.(value);
      }
    );
    vue.watch(
      () => props.selectedValue,
      (selected) => {
        setTreeCurrentKey(selected);
      }
    );
    vue.onMounted(() => {
      setTreeCurrentKey(props.selectedValue);
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleLoading, vue.mergeProps({
        loading: __props.loading,
        class: "ele-crud-tree-wrapper"
      }, __props.sideConfig?.loadingProps || {}), {
        default: vue.withCtx(() => [
          vue.createVNode(vue.unref(elementPlus.ElTree), vue.mergeProps({
            ref_key: "treeRef",
            ref: treeRef,
            data: __props.data,
            highlightCurrent: true,
            expandOnClickNode: false,
            defaultExpandAll: true,
            filterNodeMethod: filterNode,
            class: "ele-crud-tree",
            nodeKey: vue.unref(util.defaultTreeNodeKey)
          }, __props.sideConfig?.treeProps || {}, { onNodeClick: handleNodeClick }), vue.createSlots({
            empty: vue.withCtx(() => [
              vue.createVNode(vue.unref(elementPlus.ElEmpty), vue.mergeProps({
                imageSize: 68,
                description: __props.errorMessage
              }, __props.sideConfig?.emptyProps || {}), null, 16, ["description"])
            ]),
            _: 2
          }, [
            vue.renderList(vue.unref(common.getSlotsMap)(
              _ctx.$slots,
              __props.sideConfig?.treeSlots,
              ["empty"]
            ), (slotName, compSlotName) => {
              return {
                name: compSlotName,
                fn: vue.withCtx((slotProps) => [
                  vue.renderSlot(_ctx.$slots, slotName, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                ])
              };
            })
          ]), 1040, ["data", "nodeKey"])
        ]),
        _: 3
      }, 16, ["loading"]);
    };
  }
});
module.exports = _sfc_main;
