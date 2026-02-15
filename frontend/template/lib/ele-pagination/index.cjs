"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "ElePagination" },
  __name: "index",
  props: props.paginationProps,
  emits: props.paginationEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const paginationRef = vue.ref(null);
    const isInfinite = vue.computed(() => "*" === props2.total);
    const pageTotal = vue.computed(() => {
      if (isInfinite.value) {
        if (props2.hasNext) {
          return Number.MAX_SAFE_INTEGER;
        }
        return (props2.currentPage || 1) * (props2.pageSize || 10);
      }
      const num = props2.total == null ? void 0 : Number(props2.total);
      return num == null || isNaN(num) ? void 0 : num;
    });
    const sizesPopperClass = vue.computed(() => {
      const classes = ["ele-pagination-popper"];
      if (props2.isFixedPopper) {
        classes.push("is-fixed");
      }
      if (typeof props2.popperClass === "string" && props2.popperClass) {
        classes.push(props2.popperClass);
      }
      return classes.join(" ");
    });
    const handleUpdateCurrentPage = (currentPage) => {
      emit("update:currentPage", currentPage);
    };
    const handleUpdatePageSize = (pageSize) => {
      emit("update:pageSize", pageSize);
    };
    __expose({
      paginationRef
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElPagination), {
        ref_key: "paginationRef",
        ref: paginationRef,
        small: _ctx.small,
        size: _ctx.size,
        background: _ctx.type === "circle" ? false : _ctx.background,
        pageSize: _ctx.pageSize,
        defaultPageSize: _ctx.defaultPageSize,
        total: pageTotal.value,
        pageCount: _ctx.pageCount,
        pagerCount: _ctx.pagerCount,
        currentPage: _ctx.currentPage,
        defaultCurrentPage: _ctx.defaultCurrentPage,
        layout: _ctx.layout,
        pageSizes: _ctx.pageSizes,
        popperClass: sizesPopperClass.value,
        prevText: _ctx.prevText,
        prevIcon: _ctx.prevIcon,
        nextText: _ctx.nextText,
        nextIcon: _ctx.nextIcon,
        disabled: _ctx.disabled,
        teleported: _ctx.teleported,
        hideOnSinglePage: _ctx.hideOnSinglePage,
        class: vue.normalizeClass(["ele-pagination", [{ "is-circle": _ctx.type === "circle" }, { "is-infinite": isInfinite.value }]]),
        "onUpdate:currentPage": handleUpdateCurrentPage,
        "onUpdate:pageSize": handleUpdatePageSize
      }, vue.createSlots({ _: 2 }, [
        vue.renderList(Object.keys(_ctx.$slots), (name) => {
          return {
            name,
            fn: vue.withCtx((slotProps) => [
              vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
            ])
          };
        })
      ]), 1032, ["small", "size", "background", "pageSize", "defaultPageSize", "total", "pageCount", "pagerCount", "currentPage", "defaultCurrentPage", "layout", "pageSizes", "popperClass", "prevText", "prevIcon", "nextText", "nextIcon", "disabled", "teleported", "hideOnSinglePage", "class"]);
    };
  }
});
module.exports = _sfc_main;
