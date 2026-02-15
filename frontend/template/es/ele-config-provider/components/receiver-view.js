import { defineComponent as u, ref as l, computed as h, watch as w, createVNode as x } from "vue";
import I from "../../ele-watermark/index";
import { svgText as e, getProps as P, svgContents as a, svgProp as n, getOption as C } from "../../ele-watermark/util";
const k = /* @__PURE__ */ u({
  name: "ReceiverView",
  props: {
    wrapHeight: [String, Number]
  },
  setup(g, {
    slots: d
  }) {
    const o = l(), r = e[e.length - 2], {
      svgKey: i,
      svgProps: s,
      svgConfig: p,
      imageId: m
    } = P(a), v = h(() => p.key), c = n[e.findIndex((t) => t === e[e.length - 1])];
    return w(v, (t) => {
      o.value = C(t, c, s, 2, 13, r, i, a, n, n[e.findIndex((f) => f === r)]);
    }, {
      immediate: !0
    }), () => x(I, {
      width: 236,
      height: 74,
      wrapHeight: g.wrapHeight,
      disabled: !!m.value,
      fixed: !o.value,
      content: i.value,
      wrapPosition: !1,
      svgRender: !0
    }, {
      default: () => [d.default?.(s)]
    });
  }
});
export {
  k as default
};
