<template>
  <ele-page class="workplace-page">
    <el-row :gutter="10" class="workplace-row">
      <!-- 左列：Banner + 常用功能 + 我的待办 -->
      <el-col :md="16" :sm="24" :xs="24" class="workplace-col">
        <div ref="leftStackRef" class="workplace-stack">
          <banner-card ref="bannerCardRef" :height="topRowHeight" />
          <quick-action-bar />
          <todo-card title="我的待办" class="workplace-todo" />
        </div>
      </el-col>
      <!-- 右列：用户问候 + 最新动态 -->
      <el-col :md="8" :sm="24" :xs="24" class="workplace-col">
        <div class="workplace-stack workplace-stack--right">
          <profile-card ref="profileCardRef" :height="topRowHeight" />
          <activities-card
            title="最新动态"
            class="workplace-activities"
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
    WORKPLACE_STACK_BREAKPOINT
  } from './layout';

  defineOptions({
    name: 'DashboardWorkplace'
  });

  /** Banner 卡片，用于测量宽度与同步顶部行高度 */
  const bannerCardRef = ref<InstanceType<typeof BannerCard> | null>(null);
  /** 顶部用户信息 */
  const profileCardRef = ref<InstanceType<typeof ProfileCard> | null>(null);
  /** 左列容器，用于测量实际高度 */
  const leftStackRef = ref<HTMLElement>();
  /** Banner / 问候区共用高度（大屏等高） */
  const topRowHeight = ref<string>();
  /** 最新动态卡片高度（由左列高度精确计算，保证两列底部对齐） */
  const activitiesHeight = ref<string>();
  /** 右列卡片间距，与 .workplace-stack 的 gap 保持一致 */
  const STACK_GAP = 10;
  /** 小屏断点，堆叠时不强制等高 */
  const STACK_BREAKPOINT = WORKPLACE_STACK_BREAKPOINT;

  const activitiesStyle = computed<CSSProperties | undefined>(() =>
    activitiesHeight.value ? { height: activitiesHeight.value } : undefined
  );

  /** 观察左列：仅同步最新动态高度 */
  let stackObserver: ResizeObserver | null = null;
  /** 观察 Banner / 问候区：同步顶部行等高 */
  let topRowObserver: ResizeObserver | null = null;
  /** 避免测量过程中 ResizeObserver 重入导致循环 */
  let topRowSyncing = false;
  /** 最近一次无强制高度时测得的问候区自然高度 */
  let cachedProfileNatural = 0;
  /** 最近一次用于计算比例高度的 Banner 宽度 */
  let cachedBannerWidth = 0;

  const getCardEl = (
    card: { $el?: HTMLElement } | null | undefined
  ): HTMLElement | undefined => card?.$el;

  /**
   * 以左列实际高度为基准，反推最新动态卡片高度：
   * 左列高度 = 用户问候高度 + 间距 + 最新动态高度
   * 因此最新动态高度 = 左列高度 - 用户问候高度 - 间距
   */
  const syncActivitiesHeight = () => {
    if (window.innerWidth <= STACK_BREAKPOINT) {
      if (activitiesHeight.value !== undefined) {
        activitiesHeight.value = undefined;
      }
      return;
    }
    const leftEl = leftStackRef.value;
    const profileEl = getCardEl(profileCardRef.value);
    if (!leftEl || !profileEl) {
      activitiesHeight.value = undefined;
      return;
    }
    const height = leftEl.offsetHeight - profileEl.offsetHeight - STACK_GAP;
    const next = height > 0 ? `${height}px` : undefined;
    if (activitiesHeight.value !== next) {
      activitiesHeight.value = next;
    }
  };

  const observeTopRow = () => {
    if (!topRowObserver) return;
    topRowObserver.disconnect();
    const bannerEl = getCardEl(bannerCardRef.value);
    const profileEl = getCardEl(profileCardRef.value);
    if (bannerEl) topRowObserver.observe(bannerEl);
    if (profileEl) topRowObserver.observe(profileEl);
  };

  /**
   * 大屏：取 max(Banner 比例高度, 问候区自然高度) 注入两侧，保证等高；
   * 小屏：取消强制高度，Banner 按比例、问候区按内容各自自适应。
   */
  const syncTopRowHeight = async () => {
    if (topRowSyncing) return;

    if (window.innerWidth <= STACK_BREAKPOINT) {
      if (topRowHeight.value !== undefined) {
        topRowHeight.value = undefined;
      }
      cachedProfileNatural = 0;
      cachedBannerWidth = 0;
      syncActivitiesHeight();
      return;
    }

    const bannerEl = getCardEl(bannerCardRef.value);
    const profileEl = getCardEl(profileCardRef.value);
    if (!bannerEl || !profileEl) return;

    const bannerWidth = bannerEl.offsetWidth;
    if (bannerWidth <= 0) return;

    const aspectHeight = bannerWidth / BANNER_IMAGE_ASPECT_RATIO;
    const widthChanged = Math.abs(bannerWidth - cachedBannerWidth) > 1;
    const needRemeasure =
      !topRowHeight.value || widthChanged || cachedProfileNatural <= 0;

    if (!needRemeasure) {
      const target = Math.ceil(
        Math.max(aspectHeight, cachedProfileNatural)
      );
      const next = `${target}px`;
      if (topRowHeight.value !== next) {
        topRowHeight.value = next;
        await nextTick();
      }
      syncActivitiesHeight();
      return;
    }

    topRowSyncing = true;
    try {
      topRowObserver?.disconnect();

      if (topRowHeight.value !== undefined) {
        topRowHeight.value = undefined;
        await nextTick();
      }

      cachedBannerWidth = bannerWidth;
      cachedProfileNatural = profileEl.offsetHeight;
      const bannerNatural = Math.max(bannerEl.offsetHeight, aspectHeight);
      const target = Math.ceil(
        Math.max(bannerNatural, cachedProfileNatural, aspectHeight)
      );
      const next = `${target}px`;
      topRowHeight.value = next;
      await nextTick();

      syncActivitiesHeight();
      observeTopRow();
    } finally {
      topRowSyncing = false;
    }
  };

  const scheduleTopRowSync = () => {
    nextTick(() => {
      void syncTopRowHeight();
    });
  };

  const scheduleActivitiesSync = () => {
    nextTick(syncActivitiesHeight);
  };

  onMounted(() => {
    scheduleTopRowSync();

    stackObserver = new ResizeObserver(() => {
      // 快捷操作等左列内容变化时，只校正最新动态高度，避免反复清空顶部行
      if (!topRowSyncing) {
        scheduleActivitiesSync();
      }
    });
    if (leftStackRef.value) {
      stackObserver.observe(leftStackRef.value);
    }

    topRowObserver = new ResizeObserver(() => {
      scheduleTopRowSync();
    });
    observeTopRow();

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
    cachedProfileNatural = 0;
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

  /* 右列最新动态高度由 JS 依据左列实际高度精确计算并写入行内 height；
     flex:1 1 auto 让行内 height 作为 flex-basis（打破"内容撑高整行"的循环），
     grow/shrink + min-height:0 兜底保证底部与左列对齐、内部滚动 */
  .workplace-stack--right {
    .workplace-activities {
      flex: 1 1 auto;
      min-height: 0;
    }
  }

  /* 左列我的待办弹性填充剩余高度，使其底部与右列最新动态底部对齐，
     内容超出时卡片内部滚动 */
  .workplace-stack .workplace-todo {
    flex: 1 1 auto;
    min-height: 0;
  }

  /* 小屏下两列堆叠，右列间距补齐 */
  @media screen and (max-width: 992px) {
    .workplace-col + .workplace-col .workplace-stack {
      margin-top: 10px;
    }
  }
</style>
