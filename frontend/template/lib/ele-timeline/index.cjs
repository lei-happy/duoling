"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const props = require("./props");
const _hoisted_1 = ["onClick"];
const _hoisted_2 = { class: "ele-time-line-item-icon" };
const _hoisted_3 = { class: "ele-time-line-item-body" };
const _hoisted_4 = { class: "ele-time-line-item-title" };
const _hoisted_5 = { class: "ele-time-line-item-description" };
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleTimeline" },
  __name: "index",
  props: props.timelineProps,
  emits: props.timelineEmits,
  setup(__props, { emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const listRef = vue.ref(null);
    const listWidth = vue.ref(0);
    const listColNum = vue.computed(() => {
      return Math.floor(listWidth.value / props2.itemWidth) || 1;
    });
    const lineRows = vue.computed(() => {
      const rows = [];
      const data = props2.data || [];
      const colNum = listColNum.value;
      const rowNum = colNum ? Math.ceil(data.length / colNum) : 1;
      for (let i = 0; i < rowNum; i++) {
        const cells = [];
        for (let j = 0; j < colNum; j++) {
          const index2 = i * colNum + j;
          const itemData = data[index2];
          cells.push({
            key: itemData?.key ?? `${i}_${j}`,
            data: itemData,
            dataIndex: index2,
            nextDataType: data[index2 + 1]?.type,
            isFirst: itemData && index2 === 0,
            isLast: itemData && index2 === data.length - 1
          });
        }
        const key = `${i}_${cells.map((d) => d?.key ?? "").join()}`;
        rows.push({
          key,
          items: cells,
          isEvenRow: (i + 1) % 2 === 0
        });
      }
      return rows;
    });
    const handleItemClick = (item, e) => {
      if (item) {
        emit("itemClick", item, e);
      }
    };
    const observer = new ResizeObserver(() => {
      requestAnimationFrame(() => {
        const listEl = listRef.value;
        listWidth.value = listEl?.clientWidth || 0;
      });
    });
    vue.onMounted(() => {
      const listEl = listRef.value;
      listEl && observer.observe(listEl);
    });
    vue.onBeforeUnmount(() => {
      const listEl = listRef.value;
      listEl && observer.unobserve(listEl);
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("div", {
        ref_key: "listRef",
        ref: listRef,
        class: "ele-time-line-list"
      }, [
        (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(lineRows.value, (row) => {
          return vue.openBlock(), vue.createElementBlock("div", {
            key: row.key,
            class: vue.normalizeClass(["ele-time-line-row", { "is-even-row": row.isEvenRow }])
          }, [
            (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(row.items, (col) => {
              return vue.openBlock(), vue.createElementBlock("div", {
                key: col.key,
                class: vue.normalizeClass(["ele-time-line-item", [
                  { "is-first": col.isFirst },
                  { "is-last": col.isLast },
                  { "is-primary": col.data && col.data.type === "primary" },
                  { "is-danger": col.data && col.data.type === "danger" },
                  { "is-placeholder": !col.data }
                ]]),
                onClick: (e) => handleItemClick(col.data, e)
              }, [
                col.data ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
                  vue.createElementVNode("div", _hoisted_2, [
                    vue.createElementVNode("div", {
                      class: vue.normalizeClass(["ele-time-line-item-line is-start", [
                        { "is-primary-line": col.data.type === "primary" },
                        { "is-danger-line": col.data.type === "danger" }
                      ]])
                    }, null, 2),
                    vue.createVNode(vue.unref(elementPlus.ElIcon), vue.mergeProps({ class: "ele-time-line-item-icon-status" }, { ref_for: true }, col.data.iconProps || {}), {
                      default: vue.withCtx(() => [
                        vue.renderSlot(_ctx.$slots, "itemIcon", {
                          item: col.data
                        }, () => [
                          col.data.icon ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(col.data.icon), {
                            key: 0,
                            style: vue.normalizeStyle(col.data.iconStyle)
                          }, null, 8, ["style"])) : col.data.type === "danger" ? (vue.openBlock(), vue.createBlock(vue.unref(index.CloseCircleFilled), {
                            key: 1,
                            style: vue.normalizeStyle(col.data.iconStyle)
                          }, null, 8, ["style"])) : (vue.openBlock(), vue.createBlock(vue.unref(index.CheckCircleFilled), {
                            key: 2,
                            style: vue.normalizeStyle(col.data.iconStyle)
                          }, null, 8, ["style"]))
                        ])
                      ]),
                      _: 2
                    }, 1040),
                    vue.createElementVNode("div", {
                      class: vue.normalizeClass(["ele-time-line-item-line is-end", [
                        { "is-primary-line": col.nextDataType === "primary" },
                        { "is-danger-line": col.nextDataType === "danger" }
                      ]])
                    }, null, 2)
                  ]),
                  !col.isLast ? (vue.openBlock(), vue.createElementBlock("div", {
                    key: 0,
                    class: vue.normalizeClass(["ele-time-line-item-line-turn", [
                      { "is-primary-line": col.nextDataType === "primary" },
                      { "is-danger-line": col.nextDataType === "danger" }
                    ]])
                  }, null, 2)) : vue.createCommentVNode("", true),
                  vue.createElementVNode("div", _hoisted_3, [
                    vue.renderSlot(_ctx.$slots, "itemTitle", {
                      item: col.data
                    }, () => [
                      vue.createElementVNode("div", _hoisted_4, vue.toDisplayString(col.data.title), 1)
                    ]),
                    vue.renderSlot(_ctx.$slots, "itemDescription", {
                      item: col.data
                    }, () => [
                      vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(col.data.description), 1)
                    ])
                  ])
                ], 64)) : vue.createCommentVNode("", true)
              ], 10, _hoisted_1);
            }), 128))
          ], 2);
        }), 128))
      ], 512);
    };
  }
});
module.exports = _sfc_main;
