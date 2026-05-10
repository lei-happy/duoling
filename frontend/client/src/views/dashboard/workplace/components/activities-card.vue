<!-- 最新动态 -->
<template>
  <ele-card :header="title" :body-style="{ padding: '6px 0', height: '400px' }">
    <template #extra>
      <more-icon :hide-edit="true" @command="handleCommand" />
    </template>
    <el-scrollbar :view-style="{ padding: '20px 20px 0 20px' }">
      <div v-if="loading" class="activities-loading">
        <el-skeleton :rows="6" animated />
      </div>
      <el-empty v-else-if="!activities.length" description="今日暂无动态" />
      <el-timeline
        v-else
        :reverse="false"
        class="demo-timeline activities-timeline"
      >
        <el-timeline-item
          v-for="{ item, parts } in activityRows"
          :key="item.id"
          :timestamp="item.display_time"
          :color="scenarioColor(item.event_code)"
          :hollow="timelineHollow(item.event_code)"
          :style="timelineItemVars(item.event_code)"
          :class="{
            'activity-tl-item--node-dashed':
              nodeKind(item.event_code) === 'hollow-dashed'
          }"
        >
          <div
            class="activity-summary"
            :class="{ 'activity-summary--new': newPulseIds.has(item.id) }"
          >
            <template v-if="parts.actor">
              <span class="activity-summary__plain">{{ parts.before }}</span>
              <span class="activity-summary__actor">{{ parts.actor }}</span>
              <span class="activity-summary__plain">{{ parts.after }}</span>
            </template>
            <template v-else>{{ item.summary }}</template>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-scrollbar>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, onMounted, onUnmounted, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import MoreIcon from './more-icon.vue';
  import type { Command } from '../model';
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
  const newPulseIds = ref<Set<number>>(new Set());
  /** 已展示过的 id，用于检测轮询/手动刷新后的新动态 */
  const seenActivityIds = ref<Set<number>>(new Set());
  let pollTimer: ReturnType<typeof setInterval> | null = null;
  let newPulseClearTimer: number | null = null;

  /** 自动刷新间隔（毫秒） */
  const POLL_MS = 30_000;

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

  const markNewItemsAfterFetch = (items: CompanyActivityItem[]) => {
    if (newPulseClearTimer) {
      clearTimeout(newPulseClearTimer);
      newPulseClearTimer = null;
    }
    if (seenActivityIds.value.size === 0) {
      seenActivityIds.value = new Set(items.map((x) => x.id));
      return;
    }
    const arrived = new Set<number>();
    for (const it of items) {
      if (!seenActivityIds.value.has(it.id)) {
        arrived.add(it.id);
      }
    }
    seenActivityIds.value = new Set(items.map((x) => x.id));
    if (arrived.size === 0) {
      return;
    }
    newPulseIds.value = arrived;
    newPulseClearTimer = window.setTimeout(() => {
      newPulseIds.value = new Set();
      newPulseClearTimer = null;
    }, 1800);
  };

  const loadActivities = async (silent = false) => {
    if (!silent) {
      loading.value = true;
    }
    try {
      const res = await getCompanyActivities({ limit: 50 });
      const items = res.data.data?.items ?? [];
      markNewItemsAfterFetch(items);
      activities.value = items;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : '加载失败';
      EleMessage.error(msg);
    } finally {
      if (!silent) {
        loading.value = false;
      }
    }
  };

  const handleCommand = (command: Command) => {
    if (command === 'refresh') {
      loadActivities(false);
      return;
    }
    emit('command', command);
  };

  onMounted(() => {
    loadActivities(false);
    pollTimer = setInterval(() => {
      loadActivities(true);
    }, POLL_MS);
  });

  onUnmounted(() => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    if (newPulseClearTimer) {
      clearTimeout(newPulseClearTimer);
      newPulseClearTimer = null;
    }
  });
</script>

<style lang="scss" scoped>
  .activities-loading {
    padding: 8px 0;
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

  .activity-summary--new {
    position: relative;
    margin-left: -6px;
    padding-left: 8px;
    border-radius: 6px;
    animation: activity-row-highlight 1.6s ease-out 1;
  }

  @keyframes activity-row-highlight {
    0% {
      background-color: var(--el-color-primary-light-9);
      box-shadow: inset 3px 0 0 var(--el-color-primary);
    }
    55% {
      background-color: var(--el-color-primary-light-9);
      box-shadow: inset 3px 0 0 var(--el-color-primary-light-5);
    }
    100% {
      background-color: transparent;
      box-shadow: inset 3px 0 0 transparent;
    }
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
      display: flex;

      .el-timeline-item__timestamp {
        order: 0;
        flex-shrink: 0;
        margin: 1px 12px 0 0;
        height: 22px;
        line-height: 22px;
        font-size: 14px;
      }

      .el-timeline-item__content {
        order: 1;
        flex: 1;
      }
    }

    :deep(.el-timeline-item__node) {
      top: 3px;
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

    :deep(.el-timeline-item__tail) {
      top: 3px;
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
