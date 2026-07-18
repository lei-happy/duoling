<template>
  <ele-page class="workplace-page">
    <el-row :gutter="10" class="workplace-row">
      <!-- 左列：Banner + 常用功能 + 我的待办 -->
      <el-col :md="16" :sm="24" :xs="24" class="workplace-col">
        <div ref="leftStackRef" class="workplace-stack">
          <banner-card ref="bannerCardRef" :height="topRowHeight" />
          <quick-action-bar ref="quickActionBarRef" />
          <todo-card
            title="我的待办"
            class="workplace-todo"
            :class="{ 'is-region-synced': !!todoRegionHeight }"
            :style="todoRegionStyle"
          />
        </div>
      </el-col>
      <!-- 右列：用户问候 + 最新动态 -->
      <el-col :md="8" :sm="24" :xs="24" class="workplace-col">
        <div class="workplace-stack workplace-stack--right">
          <profile-card ref="profileCardRef" :height="topRowHeight" />
          <activities-card
            title="最新动态"
            class="workplace-activities"
            :class="{ 'is-region-synced': !!activitiesRegionHeight }"
            :style="activitiesStyle"
          />
        </div>
      </el-col>
    </el-row>
  </ele-page>
</template>

<script lang="ts" setup>
  import {
    ref,
    computed,
    nextTick,
    onMounted,
    onBeforeUnmount,
    onActivated
  } from 'vue';
  import type { CSSProperties } from 'vue';
  import ProfileCard from './components/profile-card.vue';
  import BannerCard from './components/banner-card.vue';
  import QuickActionBar from './components/quick-action-bar.vue';
  import ActivitiesCard from './components/activities-card.vue';
  import TodoCard from './components/todo-card.vue';
  import {
    BANNER_IMAGE_ASPECT_RATIO,
    WORKPLACE_STACK_BREAKPOINT,
    WORKPLACE_STACK_GAP,
    getTodoRegionHeightPx
  } from './layout';

  defineOptions({
    name: 'DashboardWorkplace'
  });

  /** Banner 卡片，用于测量宽度并按 5:1 定高 */
  const bannerCardRef = ref<InstanceType<typeof BannerCard> | null>(null);
  /** 顶部用户信息（跟随 Banner 高度） */
  const profileCardRef = ref<InstanceType<typeof ProfileCard> | null>(null);
  /** 左列容器，用于测量实际高度 */
  const leftStackRef = ref<HTMLElement>();
  /** 快捷操作，用于与最新动态顶部对齐 */
  const quickActionBarRef = ref<InstanceType<typeof QuickActionBar> | null>(
    null
  );
  /** Banner 定高后注入两侧，保证等高且容器恒为 5:1 */
  const topRowHeight = ref<string>();
  /** 我的待办固定高度（约 6~8 条） */
  const todoRegionHeight = ref<string>();
  /** 最新动态高度（顶对齐快捷操作、底对齐我的待办） */
  const activitiesRegionHeight = ref<string>();
  /** 小屏断点，堆叠时不强制等高 */
  const STACK_BREAKPOINT = WORKPLACE_STACK_BREAKPOINT;
  /** 卡片间距，与 .workplace-stack gap 一致 */
  const STACK_GAP = WORKPLACE_STACK_GAP;

  const todoRegionStyle = computed<CSSProperties | undefined>(() => {
    if (!todoRegionHeight.value) return undefined;
    return {
      height: todoRegionHeight.value,
      maxHeight: todoRegionHeight.value
    };
  });

  const activitiesStyle = computed<CSSProperties | undefined>(() => {
    if (!activitiesRegionHeight.value) return undefined;
    const style: CSSProperties = {
      height: activitiesRegionHeight.value,
      maxHeight: activitiesRegionHeight.value
    };
    if (activitiesTopOffset.value) {
      style.marginTop = activitiesTopOffset.value;
    }
    return style;
  });
  /** 校正 Profile 与 Banner 高度差，使最新动态顶与快捷操作对齐 */
  const activitiesTopOffset = ref<string>();

  /** 观察左列：仅同步最新动态高度 */
  let stackObserver: ResizeObserver | null = null;
  /** 观察 Banner 宽度：同步顶部行等高 */
  let topRowObserver: ResizeObserver | null = null;
  /** 最近一次用于计算比例高度的 Banner 宽度 */
  let cachedBannerWidth = 0;

  const getCardEl = (
    card: { $el?: HTMLElement } | null | undefined
  ): HTMLElement | undefined => card?.$el;

  /**
   * 待办固定一屏 6~8 条；最新动态高度 = 快捷操作高 + 间距 + 待办高，
   * 使动态顶对齐快捷操作、底对齐我的待办。
   */
  const syncStackRegionHeight = () => {
    if (window.innerWidth <= STACK_BREAKPOINT) {
      if (todoRegionHeight.value !== undefined) {
        todoRegionHeight.value = undefined;
      }
      if (activitiesRegionHeight.value !== undefined) {
        activitiesRegionHeight.value = undefined;
      }
      if (activitiesTopOffset.value !== undefined) {
        activitiesTopOffset.value = undefined;
      }
      return;
    }
    const quickEl = getCardEl(quickActionBarRef.value);
    const profileEl = getCardEl(profileCardRef.value);
    if (!quickEl) {
      todoRegionHeight.value = undefined;
      activitiesRegionHeight.value = undefined;
      activitiesTopOffset.value = undefined;
      return;
    }

    const todoHeightPx = getTodoRegionHeightPx();
    const activitiesHeightPx =
      quickEl.offsetHeight + STACK_GAP + todoHeightPx;
    const nextTodoHeight = `${todoHeightPx}px`;
    const nextActivitiesHeight = `${activitiesHeightPx}px`;

    if (todoRegionHeight.value !== nextTodoHeight) {
      todoRegionHeight.value = nextTodoHeight;
    }
    if (activitiesRegionHeight.value !== nextActivitiesHeight) {
      activitiesRegionHeight.value = nextActivitiesHeight;
    }

    if (profileEl) {
      const quickTop = quickEl.getBoundingClientRect().top;
      const naturalTop =
        profileEl.getBoundingClientRect().bottom + STACK_GAP;
      const offset = Math.round(quickTop - naturalTop);
      const nextOffset = offset !== 0 ? `${offset}px` : undefined;
      if (activitiesTopOffset.value !== nextOffset) {
        activitiesTopOffset.value = nextOffset;
      }
    }
  };

  const observeActivitiesAnchors = () => {
    if (!stackObserver) return;
    const quickEl = getCardEl(quickActionBarRef.value);
    const profileEl = getCardEl(profileCardRef.value);
    if (quickEl) stackObserver.observe(quickEl);
    if (profileEl) stackObserver.observe(profileEl);
  };

  const observeBanner = () => {
    if (!topRowObserver) return;
    topRowObserver.disconnect();
    const bannerEl = getCardEl(bannerCardRef.value);
    if (bannerEl) topRowObserver.observe(bannerEl);
  };

  /**
   * 大屏：Banner 按 5:1 定高，问候区跟随（容器恒 5:1，cover 不裁左右）；
   * 小屏：取消强制高度，Banner 自身 aspect-ratio，问候区内容自适应。
   */
  const syncTopRowHeight = () => {
    if (window.innerWidth <= STACK_BREAKPOINT) {
      if (topRowHeight.value !== undefined) {
        topRowHeight.value = undefined;
      }
      cachedBannerWidth = 0;
      syncStackRegionHeight();
      return;
    }

    const bannerEl = getCardEl(bannerCardRef.value);
    if (!bannerEl) return;

    const bannerWidth = bannerEl.offsetWidth;
    if (bannerWidth <= 0) return;

    const widthChanged = Math.abs(bannerWidth - cachedBannerWidth) > 1;
    const target = Math.ceil(bannerWidth / BANNER_IMAGE_ASPECT_RATIO);
    const next = `${target}px`;

    if (!widthChanged && topRowHeight.value === next) {
      syncStackRegionHeight();
      return;
    }

    cachedBannerWidth = bannerWidth;
    if (topRowHeight.value !== next) {
      topRowHeight.value = next;
    }
    nextTick(syncStackRegionHeight);
  };

  const scheduleTopRowSync = () => {
    nextTick(syncTopRowHeight);
  };

  const scheduleStackRegionSync = () => {
    nextTick(syncStackRegionHeight);
  };

  onMounted(() => {
    scheduleTopRowSync();

    stackObserver = new ResizeObserver(() => {
      scheduleStackRegionSync();
    });
    if (leftStackRef.value) {
      stackObserver.observe(leftStackRef.value);
    }
    nextTick(observeActivitiesAnchors);

    topRowObserver = new ResizeObserver(() => {
      scheduleTopRowSync();
    });
    observeBanner();

    window.addEventListener('resize', scheduleTopRowSync);
  });

  onBeforeUnmount(() => {
    stackObserver?.disconnect();
    stackObserver = null;
    topRowObserver?.disconnect();
    topRowObserver = null;
    window.removeEventListener('resize', scheduleTopRowSync);
  });

  /** 从其他页签返回时重新校正顶部行与右列高度 */
  onActivated(() => {
    cachedBannerWidth = 0;
    scheduleTopRowSync();
  });
</script>

<style lang="scss" scoped>
  .workplace-row {
    align-items: stretch;
    margin-bottom: 16px;
  }

  .workplace-col {
    display: flex;
    min-height: 0;
  }

  /* 每列内部纵向堆叠，卡片之间统一间距 */
  .workplace-stack {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-width: 0;
    min-height: 0;

    > :deep(.ele-card) {
      margin-bottom: 0;
    }
  }

  /* 右列最新动态：顶对齐快捷操作、底对齐我的待办，高度由 JS 写入，内部滚动 */
  .workplace-stack--right {
    .workplace-activities {
      flex: 1 1 auto;
      min-height: 0;
      overflow: hidden;

      &.is-region-synced {
        flex: 0 0 auto;
      }
    }
  }

  /* 左列我的待办：高度封顶，内容超出时卡片内部滚动 */
  .workplace-stack .workplace-todo {
    flex: 1 1 auto;
    min-height: 0;
    overflow: hidden;

    &.is-region-synced {
      flex: 0 0 auto;
    }
  }

  /* 小屏下两列堆叠，右列间距补齐 */
  @media screen and (max-width: 992px) {
    .workplace-col + .workplace-col .workplace-stack {
      margin-top: 10px;
    }
  }
</style>
