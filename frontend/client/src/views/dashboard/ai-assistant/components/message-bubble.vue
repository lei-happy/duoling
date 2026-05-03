<template>
  <div class="ai-bubble" :class="`is-${turn.role}`">
    <el-avatar :size="32" class="ai-bubble__avatar">
      <el-icon v-if="turn.role === 'user'"><user /></el-icon>
      <el-icon v-else><chat-line-square /></el-icon>
    </el-avatar>

    <div class="ai-bubble__body">
      <!-- 附件展示（仅用户消息） -->
      <div
        v-if="turn.role === 'user' && turn.attachments && turn.attachments.length"
        class="ai-bubble__attachments"
      >
        <div v-for="att in turn.attachments" :key="att.fileId" class="ai-bubble__attach">
          <el-icon><paperclip /></el-icon>
          <span class="ai-bubble__attach-name">{{ att.name }}</span>
          <span v-if="att.size" class="ai-bubble__attach-size">
            {{ formatSize(att.size) }}
          </span>
        </div>
      </div>

      <!-- 文本内容 -->
      <div v-if="turn.content" class="ai-bubble__content">
        {{ turn.content
        }}<span v-if="turn.pending && turn.role === 'assistant'" class="ai-cursor">▍</span>
      </div>

      <!-- 工具调用时间线 -->
      <div v-if="turn.toolCalls && turn.toolCalls.length" class="ai-bubble__tools">
        <tool-call-item
          v-for="tc in turn.toolCalls"
          :key="tc.toolCallId"
          :entry="tc"
          @confirm="(approved) => $emit('confirm', tc, approved)"
        />
      </div>

      <div class="ai-bubble__time">{{ turn.createdAt }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import {
    User,
    ChatLineSquare,
    Paperclip
  } from '@element-plus/icons-vue';
  import type { ChatTurn, ToolCallEntry } from '@/api/ai/model';
  import ToolCallItem from './tool-call-item.vue';

  defineProps<{ turn: ChatTurn }>();
  defineEmits<{
    (e: 'confirm', entry: ToolCallEntry, approved: boolean): void;
  }>();

  function formatSize(n: number): string {
    if (n < 1024) return `${n}B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)}KB`;
    return `${(n / 1024 / 1024).toFixed(2)}MB`;
  }
</script>

<style lang="scss" scoped>
  .ai-bubble {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;

    &.is-user {
      flex-direction: row-reverse;
      .ai-bubble__body {
        align-items: flex-end;
      }
      .ai-bubble__content {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-text-color-primary);
        border-bottom-right-radius: 2px;
      }
    }
    &.is-assistant {
      .ai-bubble__content {
        background-color: var(--el-fill-color-light);
        color: var(--el-text-color-primary);
        border-bottom-left-radius: 2px;
      }
    }

    &__avatar {
      flex: 0 0 auto;
      background-color: var(--el-color-primary-light-7);
      color: var(--el-color-primary);
    }
    &__body {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      max-width: 80%;
    }
    &__content {
      padding: 10px 14px;
      border-radius: 10px;
      line-height: 1.7;
      font-size: 14px;
      white-space: pre-wrap;
      word-break: break-word;
    }
    &__time {
      margin-top: 4px;
      font-size: 11px;
      color: var(--el-text-color-secondary);
    }
    &__attachments {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 6px;
    }
    &__attach {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 6px;
      background-color: var(--el-fill-color-light);
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
    &__attach-size {
      color: var(--el-text-color-placeholder);
    }
    &__tools {
      margin-top: 6px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      width: 100%;
    }
  }

  .ai-cursor {
    display: inline-block;
    margin-left: 2px;
    animation: blink 1s infinite;
    color: var(--el-color-primary);
  }
  @keyframes blink {
    50% {
      opacity: 0;
    }
  }
</style>
