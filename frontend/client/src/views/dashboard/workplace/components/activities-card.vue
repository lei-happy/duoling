<!-- 最新动态 -->
<template>
  <ele-card
    :header="title"
    class="activities-card"
    :body-style="{ padding: '6px 0' }"
  >
    <template #extra>
      <more-icon :hide-edit="true" @command="handleCommand" />
    </template>
    <el-scrollbar
      ref="scrollbarRef"
      :view-style="{ padding: '20px 20px 0 20px' }"
    >
      <div v-if="loading" class="activities-loading">
        <el-skeleton :rows="6" animated />
      </div>
      <el-empty v-else-if="!activities.length" description="今日暂无动态" />
      <template v-else>
        <el-timeline :reverse="false" class="demo-timeline activities-timeline">
          <el-timeline-item
            v-for="{ item, parts } in activityRows"
            :key="item.id"
            placement="top"
            :timestamp="item.display_time"
            :color="scenarioColor(item.event_code)"
            :hollow="timelineHollow(item.event_code)"
            :style="timelineItemVars(item.event_code)"
            :class="{
              'activity-tl-item--node-dashed':
                nodeKind(item.event_code) === 'hollow-dashed'
            }"
          >
            <div class="activity-summary">
              <template v-if="parts.actor">
                <span class="activity-summary__plain">{{ parts.before }}</span>
                <span class="activity-summary__actor">{{ parts.actor }}</span>
                <span class="activity-summary__plain">{{ parts.after }}</span>
              </template>
              <template v-else>{{ item.summary }}</template>
            </div>
          </el-timeline-item>
        </el-timeline>

        <div v-if="loadingMore" class="activities-load-more">
          <el-skeleton :rows="2" animated />
        </div>
        <div v-else-if="!hasMore" class="activities-no-more">
          <span>已加载全部动态</span>
        </div>
      </template>
    </el-scrollbar>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import MoreIcon from './more-icon.vue';
  import type { Command } from '../model';
  import { ACTIVITIES_PAGE_SIZE } from '../layout';
  import type { ElScrollbarInstance } from '@/components/ele-app/el';
  import {
    getCompanyActivities,
    type CompanyActivityItem
  } from '@/api/home/workbench/activities';

  defineProps<{
    title?: string;
  }>();

  const emit = defineEmits<{
    (e: 'command', command: Command): void;
  }>();

  const activities = ref<CompanyActivityItem[]>([]);
  const loading = ref(false);
  const loadingMore = ref(false);
  const currentPage = ref(1);
  const hasMore = ref(true);
  const scrollbarRef = ref<ElScrollbarInstance>(null);
  let scrollWrapEl: HTMLElement | null = null;

  /** 距底部多少 px 时触发加载下一页 */
  const SCROLL_LOAD_THRESHOLD = 80;

  type NodeKind = 'solid' | 'hollow' | 'hollow-dashed';

  /** 按 event_code 首段区分业务场景颜色（与接入规范中的域一致） */
  const scenarioColor = (eventCode: string) => {
    const domain = (eventCode.split('.')[0] || '').toLowerCase();
    const map: Record<string, string> = {
      capacity: 'var(--el-color-primary)',
      partner: 'var(--el-color-success)',
      demo: 'var(--el-color-warning)',
      waybill: '#722ed1'
    };
    return map[domain] ?? 'var(--el-color-info)';
  };

  /** 每条时间轴项注入场景色，保证空心/虚线边框与竖线同色且可被 border-color 解析 */
  const timelineItemVars = (eventCode: string) => {
    const c = scenarioColor(eventCode);
    return {
      '--activity-scenario-color': c,
      '--el-timeline-node-color': c
    } as Record<string, string>;
  };

  /** 新建/绑定类实心；修改类空心；删除/解绑类空心虚线边 */
  const nodeKind = (eventCode: string): NodeKind => {
    const c = eventCode.toLowerCase();
    if (
      c.includes('unbind') ||
      c.includes('_deleted') ||
      c.endsWith('.deleted')
    ) {
      return 'hollow-dashed';
    }
    if (
      c.includes('_created') ||
      c.endsWith('.created') ||
      (c.includes('bind') && !c.includes('unbind'))
    ) {
      return 'solid';
    }
    if (
      c.includes('_updated') ||
      c.endsWith('.updated') ||
      c.includes('assign') ||
      c.includes('task_done')
    ) {
      return 'hollow';
    }
    return 'hollow';
  };

  const timelineHollow = (eventCode: string) => nodeKind(eventCode) !== 'solid';

  const buildSummaryParts = (item: CompanyActivityItem) => {
    const actor = (item.actor_display_name || '').trim();
    if (!actor) {
      return { before: '', actor: '', after: item.summary };
    }
    const idx = item.summary.indexOf(actor);
    if (idx === -1) {
      return { before: '', actor: '', after: item.summary };
    }
    return {
      before: item.summary.slice(0, idx),
      actor,
      after: item.summary.slice(idx + actor.length)
    };
  };

  const activityRows = computed(() =>
    activities.value.map((item) => ({
      item,
      parts: buildSummaryParts(item)
    }))
  );

  const loadActivities = async (reset = false, silent = false) => {
    if (reset) {
      if (!silent) {
        loading.value = true;
      }
      currentPage.value = 1;
      hasMore.value = true;
    } else {
      if (loadingMore.value || !hasMore.value) {
        return;
      }
      loadingMore.value = true;
    }

    try {
      const res = await getCompanyActivities({
        page: currentPage.value,
        page_size: ACTIVITIES_PAGE_SIZE
      });
      const data = res.data.data;
      const items = data?.items ?? [];
      const totalPages = data?.pages ?? 1;

      if (reset) {
        activities.value = items;
      } else {
        activities.value.push(...items);
      }

      hasMore.value = currentPage.value < totalPages;
    } catch (e: unknown) {
      if (!silent) {
        const msg = e instanceof Error ? e.message : '加载失败';
        EleMessage.error(msg);
      }
    } finally {
      if (!silent) {
        loading.value = false;
      }
      loadingMore.value = false;
      await nextTick();
      attachScrollLoad();
    }
  };

  const loadMoreActivities = async () => {
    if (!hasMore.value || loadingMore.value || loading.value) {
      return;
    }
    currentPage.value += 1;
    await loadActivities(false, true);
  };

  const getScrollWrap = (): HTMLElement | null => {
    const root = scrollbarRef.value?.$el as HTMLElement | undefined;
    return root?.querySelector('.el-scrollbar__wrap') ?? null;
  };

  const tryLoadMoreOnScroll = () => {
    if (!scrollWrapEl || loading.value || loadingMore.value || !hasMore.value) {
      return;
    }
    const { scrollTop, scrollHeight, clientHeight } = scrollWrapEl;
    if (scrollHeight - scrollTop - clientHeight <= SCROLL_LOAD_THRESHOLD) {
      loadMoreActivities();
    }
  };

  const attachScrollLoad = () => {
    cleanupScrollLoad();
    scrollWrapEl = getScrollWrap();
    scrollWrapEl?.addEventListener('scroll', tryLoadMoreOnScroll, {
      passive: true
    });
  };

  const cleanupScrollLoad = () => {
    scrollWrapEl?.removeEventListener('scroll', tryLoadMoreOnScroll);
    scrollWrapEl = null;
  };

  const handleCommand = (command: Command) => {
    if (command === 'refresh') {
      loadActivities(true, false);
      return;
    }
    emit('command', command);
  };

  onMounted(() => {
    loadActivities(true, false);
  });

  onUnmounted(() => {
    cleanupScrollLoad();
  });
</script>

<style lang="scss" scoped>
  /* 高度由父级同步为与我的待办一致，内部动态列表滚动 */
  .activities-card {
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    /* 移除标题下分割线 */
    :deep(.ele-card-header) {
      border-bottom: none;
    }

    :deep(.ele-card-body) {
      flex: 1;
      min-height: 0;
      display: flex;
      flex-direction: column;
    }

    :deep(.el-scrollbar) {
      flex: 1;
      min-height: 0;
      height: 0;
    }
  }

  :deep(.ele-card-title) {
    font-size: 16px;
    font-weight: 600;
  }

  .activities-loading {
    padding: 8px 0;
  }

  .activities-load-more {
    padding: 8px 0 16px;
  }

  .activities-no-more {
    padding: 12px 0 16px;
    text-align: center;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .activity-summary {
    font-size: 14px;
    line-height: 1.55;
    color: var(--el-text-color-regular);
    border-radius: 6px;
    padding: 2px 0;
    transition: background-color 0.3s ease;
  }

  .activity-summary__actor {
    font-weight: 600;
    color: var(--el-color-primary);
  }

  /* 时间轴：同场景同色竖线 + 节点与线居中对齐 + 空心遮挡竖线 */
  .demo-timeline {
    --el-timeline-node-size-normal: 14px;
    --activities-timeline-node-size: var(--el-timeline-node-size-normal);
    /* 节点圆心与竖线几何中心对齐（竖线 left:4px、宽 2px → 中心 5px） */
    --activities-node-center-x: 5px;

    padding-left: 0;

    :deep(.el-timeline-item__node.el-timeline-item__node--normal) {
      width: var(--activities-timeline-node-size) !important;
      height: var(--activities-timeline-node-size) !important;
      min-width: var(--activities-timeline-node-size) !important;
      min-height: var(--activities-timeline-node-size) !important;
      box-sizing: border-box !important;
      left: calc(
        var(--activities-node-center-x) - var(--el-timeline-node-size-normal) /
          2
      ) !important;
    }

    :deep(.el-timeline-item__wrapper) {
      padding-left: 22px;

      /* 时间在上：加粗深色小字 */
      .el-timeline-item__timestamp {
        margin: 0 0 4px;
        line-height: 20px;
        font-size: 13px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .el-timeline-item__content {
        line-height: 1.55;
      }
    }

    :deep(.el-timeline-item__node) {
      top: 4px;
      --el-color-white: var(--el-bg-color);
    }

    /* 实心：显式使用场景色（与 hollow 一致） */
    :deep(.el-timeline-item__node:not(.is-hollow)) {
      background-color: var(
        --activity-scenario-color,
        var(--el-timeline-node-color)
      ) !important;
      border-color: var(
        --activity-scenario-color,
        var(--el-timeline-node-color)
      ) !important;
    }

    /* 空心：不透底遮挡竖线 + 描边为场景色 */
    :deep(.el-timeline-item__node.is-hollow) {
      background-color: var(
        --el-fill-color-blank,
        var(--el-bg-color)
      ) !important;
      border-style: solid !important;
      border-width: 2px !important;
      border-color: var(
        --activity-scenario-color,
        var(--el-timeline-node-color)
      ) !important;
    }

    /* 虚线竖轴 */
    :deep(.el-timeline-item__tail) {
      top: 4px;
      left: 4px;
      border-left-style: dashed;
      border-left-color: var(--el-border-color);
    }

    /* 解绑/删除：虚线边框，仍为场景色；中心不透明显示以挡住竖线 */
    :deep(.activity-tl-item--node-dashed .el-timeline-item__node) {
      background-color: var(
        --el-fill-color-blank,
        var(--el-bg-color)
      ) !important;
      border-style: dashed !important;
      border-width: 2px !important;
      border-color: var(
        --activity-scenario-color,
        var(--el-timeline-node-color)
      ) !important;
    }
  }
</style>
