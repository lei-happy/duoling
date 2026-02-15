"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const timelineProps = {
  /** 数据 */
  data: Array,
  /** 每项最小宽度 */
  itemWidth: {
    type: Number,
    default: 168
  }
};
const timelineEmits = {
  itemClick: (_item, _e) => true
};
exports.timelineEmits = timelineEmits;
exports.timelineProps = timelineProps;
