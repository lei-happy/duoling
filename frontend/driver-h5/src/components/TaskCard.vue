<template>
  <div class="task-card" @click="$emit('click')">
    <div class="task-card__header">
      <span class="task-no">{{ task.taskNo }}</span>
      <StatusTag :label="statusInfo.label" :level="statusInfo.level" />
    </div>
    <div class="task-card__route">
      <van-icon name="location-o" />
      <span class="text-ellipsis">{{ task.origin || '-' }}</span>
      <van-icon name="arrow" class="route-arrow" />
      <span class="text-ellipsis">{{ task.destination || '-' }}</span>
    </div>
    <div class="task-card__meta">
      <span>
        <van-icon name="clock-o" />
        {{ formatDateTime(task.plannedLoadTime) }}
      </span>
      <span v-if="task.totalQuantity">
        <van-icon name="logistics" />
        {{ task.totalQuantity }} 台
      </span>
    </div>
    <div v-if="task.customerName || task.plateNumber" class="task-card__footer">
      <span v-if="task.customerName" class="text-muted text-ellipsis">{{ task.customerName }}</span>
      <span v-if="task.plateNumber" class="plate">{{ task.plateNumber }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import StatusTag from './StatusTag.vue';
import type { TaskListItem } from '@/api/task';
import { formatDateTime } from '@/utils/format';
import { getDriverDisplayStatus } from '@/views/task/status-config';

const props = defineProps<{ task: TaskListItem }>();

defineEmits<{ (e: 'click'): void }>();

const statusInfo = computed(() =>
  getDriverDisplayStatus(props.task.status, props.task.accepted)
);
</script>

<style lang="scss" scoped>
.task-card {
  background: $bg-card;
  border-radius: $border-radius-md;
  padding: $spacing-lg;
  margin: $spacing-md $spacing-lg 0;
  box-shadow: $shadow-card;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: $spacing-sm;
  }

  .task-no {
    font-size: $font-size-md;
    font-weight: 600;
    color: $text-primary;
  }

  &__route {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: $font-size-md;
    color: $text-primary;
    margin-bottom: $spacing-sm;
    .text-ellipsis {
      max-width: 36%;
    }
    .route-arrow {
      color: $text-muted;
      flex-shrink: 0;
    }
    :deep(.van-icon) {
      color: $brand-primary;
      flex-shrink: 0;
    }
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    font-size: $font-size-sm;
    color: $text-secondary;
    span {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
  }

  &__footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: $spacing-sm;
    padding-top: $spacing-sm;
    border-top: 1px solid $border-color;
    font-size: $font-size-sm;
    .plate {
      background: rgba(29, 78, 216, 0.08);
      color: $brand-primary;
      padding: 2px 6px;
      border-radius: $border-radius-sm;
      font-weight: 600;
    }
  }
}
</style>
