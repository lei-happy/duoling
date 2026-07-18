/** 推广 Banner 图片宽高比（宽 / 高），与运营端上传规范 5:1 对齐 */
export const BANNER_IMAGE_ASPECT_RATIO = 5;

/** Banner 内容区四周白边（margin 2px × 2） */
export const BANNER_MARGIN = 4;

/** 工作台两列布局断点，与 index.vue 保持一致 */
export const WORKPLACE_STACK_BREAKPOINT = 992;

/** 卡片间距，与 .workplace-stack gap 一致 */
export const WORKPLACE_STACK_GAP = 10;

/** 我的待办一屏展示条数（6~8 条取中值） */
export const TODO_VISIBLE_COUNT = 7;

/** 单条待办预估高度（px，含分隔线与内边距） */
export const TODO_ITEM_ESTIMATED_HEIGHT = 76;

/** 待办卡片头部等非列表区域预估高度（px） */
export const TODO_CARD_CHROME_HEIGHT = 54;

/** 我的待办区域固定高度（px） */
export function getTodoRegionHeightPx(): number {
  return (
    TODO_CARD_CHROME_HEIGHT + TODO_ITEM_ESTIMATED_HEIGHT * TODO_VISIBLE_COUNT
  );
}

/** 我的待办列表每页条数（与一屏条数一致） */
export const TODO_PAGE_SIZE = TODO_VISIBLE_COUNT;

/** 最新动态列表每页条数（滚动加载） */
export const ACTIVITIES_PAGE_SIZE = 15;
