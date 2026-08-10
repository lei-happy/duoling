<!-- 任务时间流：状态事件为主轴，装卸记录作为子节点挂在所属阶段下 -->
<template>
  <el-empty
    v-if="!nodes.length"
    description="这条任务还没有产生流转记录"
    :image-size="80"
  />
  <el-timeline v-else class="task-timeline">
    <el-timeline-item
      v-for="node in nodes"
      :key="node.event.id"
      :type="node.tone"
      :hollow="node.isRevert"
      :timestamp="formatDateTime(node.event.eventTime) || '--'"
      placement="top"
    >
      <div class="task-timeline__card">
        <div class="task-timeline__head">
          <span class="task-timeline__title">
            {{ node.event.eventTypeLabel }}
          </span>
          <el-tag
            v-if="node.event.toStatusLabel"
            size="small"
            :type="node.isRevert ? 'danger' : 'info'"
            effect="plain"
          >
            {{ node.event.toStatusLabel }}
          </el-tag>
          <span class="ele-text-secondary task-timeline__meta">
            {{ node.event.operatorName || node.event.sourceLabel }}
          </span>
          <span v-if="node.gapText" class="ele-text-secondary">
            · 距上一步 {{ node.gapText }}
          </span>
        </div>

        <div v-if="node.event.reason" class="task-timeline__reason">
          {{ node.event.reason }}
        </div>

        <div v-if="node.payloadText" class="ele-text-secondary">
          {{ node.payloadText }}
        </div>

        <div v-if="node.records.length" class="task-timeline__records">
          <div
            v-for="rec in node.records"
            :key="rec.id"
            class="task-timeline__record"
          >
            <el-tag
              size="small"
              :type="rec.eventType === 1 ? 'warning' : 'success'"
            >
              {{ rec.eventType === 1 ? '装车' : '卸车' }}
            </el-tag>
            <span>{{ formatDateTime(rec.happenedAt) || '--' }}</span>
            <span class="ele-text-secondary">
              {{ rec.location || '--' }} · {{ rec.quantity || 0 }} 台 ·
              {{ rec.operatorName || '--' }}
            </span>
            <el-image
              v-for="(url, idx) in rec.photoUrls || []"
              :key="url"
              :src="url"
              fit="cover"
              class="task-timeline__photo"
              :preview-src-list="rec.photoUrls"
              :initial-index="idx"
            />
          </div>
        </div>
      </div>
    </el-timeline-item>
  </el-timeline>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import type {
    TaskLoadingRecord,
    TaskStatusEvent
  } from '@/api/operation/task/model';
  import { formatDateTime } from '@/utils/date-util';

  const props = defineProps<{
    events: TaskStatusEvent[];
    records: TaskLoadingRecord[];
  }>();

  /** 逆向事件（撤销 / 取消）用空心红点，与正向推进区分 */
  const REVERT_EVENT_TYPES = [9, 11, 12, 13, 14, 15, 16];

  type TimelineNode = {
    event: TaskStatusEvent;
    records: TaskLoadingRecord[];
    tone: 'primary' | 'success' | 'danger';
    isRevert: boolean;
    gapText: string;
    payloadText: string;
  };

  const humanizeGap = (ms: number): string => {
    const minutes = Math.floor(ms / 60000);
    if (minutes < 1) return '';
    if (minutes < 60) return `${minutes} 分钟`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      const rest = minutes % 60;
      return rest ? `${hours} 小时 ${rest} 分` : `${hours} 小时`;
    }
    const days = Math.floor(hours / 24);
    const restHours = hours % 24;
    return restHours ? `${days} 天 ${restHours} 小时` : `${days} 天`;
  };

  const describePayload = (payload?: Record<string, any> | null): string => {
    if (!payload) return '';
    const parts = [
      payload.carrierName,
      payload.mainDriverName,
      payload.plateNumber
    ].filter((v) => !!v);
    return parts.length ? parts.join(' · ') : '';
  };

  const nodes = computed<TimelineNode[]>(() => {
    const events = [...(props.events || [])].sort(
      (a, b) => Date.parse(a.eventTime) - Date.parse(b.eventTime)
    );
    if (!events.length) return [];

    // 装卸记录按发生时间归属到它之前最近的那个状态事件
    const buckets: TaskLoadingRecord[][] = events.map(() => []);
    [...(props.records || [])]
      .sort((a, b) => Date.parse(a.happenedAt) - Date.parse(b.happenedAt))
      .forEach((rec) => {
        const at = Date.parse(rec.happenedAt);
        let idx = 0;
        for (let i = 0; i < events.length; i++) {
          if (Date.parse(events[i].eventTime) <= at) idx = i;
          else break;
        }
        buckets[idx].push(rec);
      });

    return events.map((event, i) => {
      const isRevert = REVERT_EVENT_TYPES.includes(event.eventType);
      const prev = i > 0 ? events[i - 1] : null;
      return {
        event,
        records: buckets[i],
        tone: isRevert ? 'danger' : i === events.length - 1 ? 'primary' : 'success',
        isRevert,
        gapText: prev
          ? humanizeGap(Date.parse(event.eventTime) - Date.parse(prev.eventTime))
          : '',
        payloadText: describePayload(event.payload)
      };
    });
  });
</script>

<style lang="scss" scoped>
  .task-timeline__card {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .task-timeline__head {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .task-timeline__title {
    font-weight: 600;
  }

  .task-timeline__meta {
    font-size: 13px;
  }

  .task-timeline__reason {
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .task-timeline__records {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 4px;
    padding-left: 10px;
    border-left: 2px solid var(--el-border-color-lighter);
  }

  .task-timeline__record {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 13px;
  }

  .task-timeline__photo {
    width: 40px;
    height: 40px;
    border-radius: 4px;
  }
</style>
