"use strict";
const vue = require("vue");
const TableBody = require("./components/table-body");
const props = require("./props");
const _hoisted_1 = { class: "ele-tree-table-row" };
const _hoisted_2 = {
  key: 1,
  class: "ele-tree-table-empty"
};
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTreeTable" },
  __name: "index",
  props: props.treeTableProps,
  setup(__props) {
    const props2 = __props;
    const tableRef = vue.ref(null);
    const depth = vue.ref(1);
    const isPingLeft = vue.ref(false);
    const isPingRight = vue.ref(false);
    const checkTableScrollPing = (el) => {
      if (el) {
        const scrollLeft = el.scrollLeft;
        isPingLeft.value = scrollLeft > 1;
        const scrollWidth = el.scrollWidth - el.offsetWidth - 1;
        isPingRight.value = scrollWidth > 1 && scrollLeft < scrollWidth;
      }
    };
    const handleTableScroll = (e) => {
      checkTableScrollPing(e.currentTarget);
    };
    const getTreeDepth = (data, level = 0) => {
      let maxDepth = 0;
      if (data) {
        data.forEach((row) => {
          if (row.children && row.children.length) {
            const depth2 = getTreeDepth(row.children, level + 1);
            maxDepth = Math.max(maxDepth, depth2);
          }
        });
      }
      return maxDepth + 1;
    };
    vue.watch(
      () => props2.data,
      (data) => {
        depth.value = getTreeDepth(data);
      },
      {
        immediate: true,
        deep: true
      }
    );
    vue.watch(
      () => props2.columns,
      () => {
        vue.nextTick(() => {
          checkTableScrollPing(tableRef.value);
        });
      },
      { deep: true }
    );
    vue.onMounted(() => {
      checkTableScrollPing(tableRef.value);
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        class: vue.normalizeClass(["ele-tree-table-wrapper", [{ "is-ping-left": isPingLeft.value }, { "is-ping-right": isPingRight.value }]])
      }, [
        vue.createElementVNode("div", {
          ref_key: "tableRef",
          ref: tableRef,
          class: "ele-tree-table",
          style: vue.normalizeStyle({ height: _ctx.height }),
          onScroll: handleTableScroll
        }, [
          vue.createElementVNode("div", {
            class: "ele-tree-table-main",
            style: vue.normalizeStyle(_ctx.tableStyle)
          }, [
            vue.createElementVNode("div", {
              class: "ele-tree-table-header",
              style: vue.normalizeStyle(_ctx.headerStyle)
            }, [
              vue.createElementVNode("div", _hoisted_1, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(depth.value, (num) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: num,
                    style: vue.normalizeStyle({
                      width: `${_ctx.indexColWidth}px`,
                      left: `${(num - 1) * _ctx.indexColWidth}px`
                    }),
                    class: vue.normalizeClass(["ele-tree-table-cell is-tree-index is-fixed-left", [
                      { "is-placeholder": num !== 1 },
                      { "is-fixed-left-last": num === depth.value }
                    ]])
                  }, null, 6);
                }), 128)),
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(_ctx.columns || [], (col) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: col.key ?? col.prop,
                    style: vue.normalizeStyle(col.style),
                    class: vue.normalizeClass(["ele-tree-table-cell", col.class])
                  }, [
                    vue.renderSlot(_ctx.$slots, "headerCell", { column: col }, () => [
                      vue.createTextVNode(vue.toDisplayString(col.label), 1)
                    ])
                  ], 6);
                }), 128))
              ])
            ], 4),
            _ctx.data && _ctx.data.length ? (vue.openBlock(), vue.createBlock(TableBody, {
              key: 0,
              data: _ctx.data,
              columns: _ctx.columns || [],
              level: 1,
              depth: depth.value,
              indexColWidth: _ctx.indexColWidth,
              class: "ele-tree-table-body"
            }, vue.createSlots({ _: 2 }, [
              vue.renderList(Object.keys(_ctx.$slots), (name) => {
                return {
                  name,
                  fn: vue.withCtx((slotProps) => [
                    vue.renderSlot(_ctx.$slots, name, vue.normalizeProps(vue.guardReactiveProps(slotProps || {})))
                  ])
                };
              })
            ]), 1032, ["data", "columns", "depth", "indexColWidth"])) : (vue.openBlock(), vue.createElementBlock("div", _hoisted_2, "无数据"))
          ], 4)
        ], 36)
      ], 2);
    };
  }
});
module.exports = _sfc_main;
