"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const hook = require("../utils/hook");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleCard" },
  __name: "index",
  props: props.cardProps,
  emits: props.cardEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const {
      handleBeforeEnter,
      handleEnter,
      handleAfterEnter,
      handleBeforeLeave,
      handleLeave,
      handleAfterLeave
    } = hook.useCollapseAnim();
    const isCollapse = vue.ref(!!props2.collapse);
    const handleCollapseClick = () => {
      isCollapse.value = !isCollapse.value;
      emit("collapseChange", isCollapse.value);
    };
    const handleHeaderClick = () => {
      if (props2.collapsable === "header") {
        handleCollapseClick();
      }
    };
    vue.watch(
      () => props2.collapse,
      (collapse) => {
        if (isCollapse.value !== !!collapse) {
          isCollapse.value = !!collapse;
        }
      }
    );
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-card", [
          { "is-border": _ctx.bordered },
          { "is-shadow": _ctx.shadow === "always" },
          { "is-hover-shadow": _ctx.shadow === "hover" },
          { "is-collapse": isCollapse.value },
          { "is-flex-table": _ctx.flexTable && _ctx.flexTable !== "auto" },
          { "is-flex-auto-table": _ctx.flexTable === "auto" },
          { "is-search-form": _ctx.searchForm }
        ]])
      }, [
        _ctx.header || _ctx.$slots.header || _ctx.$slots.extra ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 0,
          class: vue.normalizeClass(["ele-card-header", _ctx.headerClass]),
          style: vue.normalizeStyle(_ctx.headerStyle),
          onClick: handleHeaderClick
        }, [
          vue.createElementVNode("div", {
            class: "ele-card-title",
            style: vue.normalizeStyle(_ctx.titleStyle)
          }, [
            vue.renderSlot(_ctx.$slots, "header", {}, () => [
              vue.createTextVNode(vue.toDisplayString(_ctx.header), 1)
            ])
          ], 4),
          _ctx.$slots.extra ? vue.renderSlot(_ctx.$slots, "extra", { key: 0 }) : vue.createCommentVNode("", true),
          _ctx.collapsable ? (vue.openBlock(), vue.createElementBlock("div", {
            key: 1,
            style: vue.normalizeStyle(_ctx.collapseIconStyle),
            class: "ele-card-collapse-icon",
            onClick: vue.withModifiers(handleCollapseClick, ["stop"])
          }, [
            vue.renderSlot(_ctx.$slots, "collapseIcon", { collapse: isCollapse.value }, () => [
              vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.ArrowUp))
                ]),
                _: 1
              })
            ])
          ], 4)) : vue.createCommentVNode("", true)
        ], 6)) : vue.createCommentVNode("", true),
        vue.createVNode(vue.Transition, {
          name: "ele-card-slide",
          onBeforeLeave: vue.unref(handleBeforeLeave),
          onLeave: vue.unref(handleLeave),
          onAfterLeave: vue.unref(handleAfterLeave),
          onBeforeEnter: vue.unref(handleBeforeEnter),
          onEnter: vue.unref(handleEnter),
          onAfterEnter: vue.unref(handleAfterEnter)
        }, {
          default: vue.withCtx(() => [
            vue.withDirectives(vue.createElementVNode("div", {
              class: vue.normalizeClass(["ele-card-body", _ctx.bodyClass]),
              style: vue.normalizeStyle(_ctx.bodyStyle)
            }, [
              vue.renderSlot(_ctx.$slots, "default")
            ], 6), [
              [vue.vShow, !isCollapse.value]
            ])
          ]),
          _: 3
        }, 8, ["onBeforeLeave", "onLeave", "onAfterLeave", "onBeforeEnter", "onEnter", "onAfterEnter"]),
        _ctx.footer || _ctx.$slots.footer ? (vue.openBlock(), vue.createElementBlock("div", {
          key: 1,
          class: vue.normalizeClass(["ele-card-footer", _ctx.footerClass]),
          style: vue.normalizeStyle(_ctx.footerStyle)
        }, [
          vue.renderSlot(_ctx.$slots, "footer", {}, () => [
            vue.createTextVNode(vue.toDisplayString(_ctx.footer), 1)
          ])
        ], 6)) : vue.createCommentVNode("", true)
      ], 2);
    };
  }
});
module.exports = _sfc_main;
