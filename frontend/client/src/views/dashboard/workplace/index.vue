<template>
  <ele-page class="workplace-page">
    <el-row :gutter="10" class="workplace-row">
      <!-- 左列：Banner + 常用功能 + 我的待办 -->
      <el-col :md="16" :sm="24" :xs="24" class="workplace-col">
        <div ref="leftStackRef" class="workplace-stack">
          <banner-card />
          <quick-action-bar />
          <todo-card title="我的待办" class="workplace-todo" />
        </div>
      </el-col>
      <!-- 右列：用户问候 + 最新动态 -->
      <el-col :md="8" :sm="24" :xs="24" class="workplace-col">
        <div class="workplace-stack workplace-stack--right">
          <profile-card ref="profileCardRef" />
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

  defineOptions({
    name: 'DashboardWorkplace'
  });

  /** 顶部用户信息 + 今日需关注 */
  const profileCardRef = ref<InstanceType<typeof ProfileCard> | null>(null);
  /** 左列容器，用于测量实际高度 */
  const leftStackRef = ref<HTMLElement>();
  /** 最新动态卡片高度（由左列高度精确计算，保证两列底部对齐） */
  const activitiesHeight = ref<string>();
  /** 右列卡片间距，与 .workplace-stack 的 gap 保持一致 */
  const STACK_GAP = 10;
  /** 小屏断点，堆叠时不强制等高 */
  const STACK_BREAKPOINT = 992;

  const activitiesStyle = computed<CSSProperties | undefined>(() =>
    activitiesHeight.value ? { height: activitiesHeight.value } : undefined
  );

  /**
   * 以左列实际高度为基准，反推最新动态卡片高度：
   * 左列高度 = 用户问候高度 + 间距 + 最新动态高度
   * 因此最新动态高度 = 左列高度 - 用户问候高度 - 间距
   * 这样右列底部始终与左列（我的待办）底部对齐，内容超出时卡片内部滚动。
   */
  const syncActivitiesHeight = () => {
    // 小屏堆叠时使用组件自身高度，不做等高处理
    if (window.innerWidth <= STACK_BREAKPOINT) {
      activitiesHeight.value = undefined;
      return;
    }
    const leftEl = leftStackRef.value;
    const profileEl = profileCardRef.value?.$el as HTMLElement | undefined;
    if (!leftEl || !profileEl) {
      activitiesHeight.value = undefined;
      return;
    }
    const height = leftEl.offsetHeight - profileEl.offsetHeight - STACK_GAP;
    activitiesHeight.value = height > 0 ? `${height}px` : undefined;
  };

  let resizeObserver: ResizeObserver | null = null;

  onMounted(() => {
    nextTick(syncActivitiesHeight);
    resizeObserver = new ResizeObserver(() => syncActivitiesHeight());
    if (leftStackRef.value) {
      resizeObserver.observe(leftStackRef.value);
    }
    const profileEl = profileCardRef.value?.$el as HTMLElement | undefined;
    if (profileEl) {
      resizeObserver.observe(profileEl);
    }
    window.addEventListener('resize', syncActivitiesHeight);
  });

  onBeforeUnmount(() => {
    resizeObserver?.disconnect();
    resizeObserver = null;
    window.removeEventListener('resize', syncActivitiesHeight);
  });

  /** 从其他页签返回时刷新今日需关注指标并重新校正高度 */
  onActivated(() => {
    profileCardRef.value?.reloadMetrics?.();
    nextTick(syncActivitiesHeight);
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

  /* 小屏下两列堆叠，右列间距补齐 */
  @media screen and (max-width: 992px) {
    .workplace-col + .workplace-col .workplace-stack {
      margin-top: 10px;
    }
  }
</style>
