"use strict";
const vue = require("vue");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "FileSort" },
  __name: "file-sort",
  props: {
    /** 当前排序字段 */
    sort: String,
    /** 当前排序方式 */
    order: String,
    /** 排序字段名称 */
    name: {
      type: String,
      required: true
    }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createElementBlock("i", {
        class: vue.normalizeClass(["ele-file-list-item-sort", [
          { "is-asc": __props.name === __props.sort && "asc" === __props.order },
          { "is-desc": __props.name === __props.sort && "desc" === __props.order }
        ]])
      }, null, 2);
    };
  }
});
module.exports = _sfc_main;
