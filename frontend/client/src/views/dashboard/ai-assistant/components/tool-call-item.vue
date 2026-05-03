<template>
  <div class="ai-tool-card" :class="`is-${entry.status}`">
    <div class="ai-tool-card__header" @click="expanded = !expanded">
      <el-icon class="ai-tool-card__icon">
        <loading v-if="entry.status === 'calling'" />
        <warning v-else-if="entry.status === 'pending_confirm'" />
        <circle-check v-else-if="entry.status === 'success'" />
        <circle-close
          v-else-if="entry.status === 'failed' || entry.status === 'denied'"
        />
        <minus v-else-if="entry.status === 'cancelled'" />
        <tools v-else />
      </el-icon>
      <span class="ai-tool-card__name">
        {{ entry.toolName || entry.toolCode }}
      </span>
      <el-tag
        v-if="entry.riskLevel === 'high'"
        size="small"
        type="warning"
        effect="light"
      >
        高风险
      </el-tag>
      <span class="ai-tool-card__status">{{ statusText }}</span>
      <span v-if="entry.latencyMs" class="ai-tool-card__latency">
        {{ entry.latencyMs }}ms
      </span>
      <el-icon class="ai-tool-card__caret">
        <arrow-down v-if="!expanded" />
        <arrow-up v-else />
      </el-icon>
    </div>

    <div v-if="expanded" class="ai-tool-card__detail">
      <div v-if="entry.params" class="ai-tool-card__section">
        <div class="ai-tool-card__section-title">入参</div>
        <pre class="ai-tool-card__pre">{{ jsonStringify(entry.params) }}</pre>
      </div>
      <div v-if="entry.summary" class="ai-tool-card__section">
        <div class="ai-tool-card__section-title">结果摘要</div>
        <pre class="ai-tool-card__pre">{{ entry.summary }}</pre>
      </div>
      <div v-if="entry.error" class="ai-tool-card__section">
        <div class="ai-tool-card__section-title">错误</div>
        <pre class="ai-tool-card__pre is-error">{{ entry.error }}</pre>
      </div>
    </div>

    <!-- 高风险待确认操作栏 -->
    <div
      v-if="entry.status === 'pending_confirm'"
      class="ai-tool-card__confirm-bar"
    >
      <span class="ai-tool-card__confirm-tip">
        请确认是否执行该高风险操作：{{ entry.toolName || entry.toolCode }}
      </span>
      <el-button size="small" @click="$emit('confirm', false)">
        取消
      </el-button>
      <el-button size="small" type="primary" @click="$emit('confirm', true)">
        确认执行
      </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import {
    Loading,
    Warning,
    CircleCheck,
    CircleClose,
    Minus,
    Tools,
    ArrowDown,
    ArrowUp
  } from '@element-plus/icons-vue';
  import type { ToolCallEntry } from '@/api/ai/model';

  const props = defineProps<{ entry: ToolCallEntry }>();
  defineEmits<{ (e: 'confirm', approved: boolean): void }>();

  const expanded = ref(false);

  const statusText = computed(() => {
    switch (props.entry.status) {
      case 'calling':
        return '调用中…';
      case 'success':
        return '成功';
      case 'failed':
        return '失败';
      case 'denied':
        return '权限拒绝';
      case 'pending_confirm':
        return '待确认';
      case 'cancelled':
        return '已取消';
      default:
        return '';
    }
  });

  function jsonStringify(v: any): string {
    try {
      return JSON.stringify(v, null, 2);
    } catch {
      return String(v);
    }
  }
</script>

<style lang="scss" scoped>
  .ai-tool-card {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background: var(--el-bg-color);
    overflow: hidden;

    &.is-success {
      border-color: var(--el-color-success-light-5);
    }
    &.is-failed,
    &.is-denied {
      border-color: var(--el-color-danger-light-5);
    }
    &.is-pending_confirm {
      border-color: var(--el-color-warning-light-5);
      background: var(--el-color-warning-light-9);
    }

    &__header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 13px;
      &:hover {
        background-color: var(--el-fill-color-lighter);
      }
    }
    &__icon {
      font-size: 16px;
    }
    &__name {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    &__status {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__latency {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }
    &__caret {
      margin-left: auto;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__detail {
      padding: 0 12px 8px;
      border-top: 1px dashed var(--el-border-color-lighter);
    }
    &__section {
      margin-top: 8px;
      &-title {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-bottom: 4px;
      }
    }
    &__pre {
      margin: 0;
      padding: 8px 10px;
      background: var(--el-fill-color-light);
      border-radius: 4px;
      font-size: 12px;
      max-height: 240px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-all;
      &.is-error {
        color: var(--el-color-danger);
      }
    }
    &__confirm-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-top: 1px solid var(--el-border-color-lighter);
      background: var(--el-color-warning-light-9);
    }
    &__confirm-tip {
      flex: 1;
      font-size: 13px;
      color: var(--el-color-warning-dark-2);
    }
  }
</style>
