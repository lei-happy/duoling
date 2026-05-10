<!-- 最新动态 -->
<template>
  <ele-card :header="title" :body-style="{ padding: '6px 0', height: '400px' }">
    <template #extra>
      <more-icon @command="handleCommand" />
    </template>
    <el-scrollbar :view-style="{ padding: '20px 20px 0 20px' }">
      <div v-if="loading" class="activities-loading">
        <el-skeleton :rows="6" animated />
      </div>
      <el-empty v-else-if="!activities.length" description="今日暂无动态" />
      <el-timeline v-else :reverse="false" class="demo-timeline">
        <el-timeline-item
          v-for="item in activities"
          :key="item.id"
          :timestamp="item.display_time"
          :type="timelineType(item.event_code)"
          :hollow="hollowFor(item.event_code)"
        >
          {{ item.summary }}
        </el-timeline-item>
      </el-timeline>
    </el-scrollbar>
  </ele-card>
</template>

<script lang="ts" setup>
  import { onMounted, onUnmounted, ref } from 'vue';
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
  let pollTimer: ReturnType<typeof setInterval> | null = null;

  const POLL_MS = 60_000;

  /** 时间轴节点颜色：与 demo / 运力等区分 */
  const timelineType = (eventCode: string) => {
    if (eventCode.startsWith('capacity.')) return 'primary';
    if (eventCode.startsWith('partner.')) return 'success';
    if (eventCode.startsWith('demo.')) return undefined;
    return undefined;
  };

  const hollowFor = (eventCode: string) => {
    if (eventCode.startsWith('capacity.')) return false;
    if (eventCode.startsWith('partner.')) return false;
    return true;
  };

  const loadActivities = async (silent = false) => {
    if (!silent) {
      loading.value = true;
    }
    try {
      const res = await getCompanyActivities({ limit: 50 });
      activities.value = res.data.data?.items ?? [];
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
  });
</script>

<style lang="scss" scoped>
  .activities-loading {
    padding: 8px 0;
  }

  /* 时间轴 */
  .demo-timeline {
    padding-left: 0;

    :deep(.el-timeline-item__wrapper) {
      display: flex;

      .el-timeline-item__timestamp {
        order: 0;
        flex-shrink: 0;
        margin: 0 16px 0 0;
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

    :deep(.el-timeline-item__tail) {
      top: 3px;
    }
  }
</style>
