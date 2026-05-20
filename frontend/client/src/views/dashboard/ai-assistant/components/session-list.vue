<template>
  <div class="ai-session-list">
    <div class="ai-session-list__header">
      <span>历史会话</span>
      <el-button text size="small" :icon="PlusOutlined" @click="$emit('new')">
        新会话
      </el-button>
    </div>
    <div
      v-for="s in sessions"
      :key="s.id"
      class="ai-session-item"
      :class="{ 'is-active': s.id === modelValue }"
      @click="$emit('update:modelValue', s.id)"
    >
      <div class="ai-session-item__title" :title="s.title || `会话 ${s.id}`">
        {{ s.title || `会话 ${s.id}` }}
      </div>
      <div class="ai-session-item__meta">
        <span class="ai-session-item__emp">{{
          s.employeeName || s.employeeCode
        }}</span>
        <span class="ai-session-item__time">{{
          formatRelative(s.lastMessageAt)
        }}</span>
      </div>
      <div class="ai-session-item__actions" @click.stop>
        <el-tooltip content="重命名" placement="top">
          <el-icon class="ai-session-item__action" @click="onRename(s)">
            <edit-outlined />
          </el-icon>
        </el-tooltip>
        <el-tooltip content="删除" placement="top">
          <el-icon
            class="ai-session-item__action ai-session-item__action--danger"
            @click="$emit('delete', s.id)"
          >
            <delete-outlined />
          </el-icon>
        </el-tooltip>
      </div>
    </div>
    <ele-text v-if="!sessions.length" type="placeholder" style="padding: 12px">
      暂无历史会话
    </ele-text>
  </div>
</template>

<script lang="ts" setup>
  import { ElMessage, ElMessageBox } from 'element-plus';
  import {
    Plus as PlusOutlined,
    Delete as DeleteOutlined,
    Edit as EditOutlined
  } from '@element-plus/icons-vue';
  import type { AiSession } from '@/api/ai/model';

  defineProps<{
    sessions: AiSession[];
    modelValue?: number | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:modelValue', id: number): void;
    (e: 'new'): void;
    (e: 'delete', id: number): void;
    (e: 'rename', id: number, title: string): void;
  }>();

  async function onRename(s: AiSession) {
    try {
      const { value } = await ElMessageBox.prompt(
        '新的会话名称',
        '重命名会话',
        {
          inputValue: s.title || `会话 ${s.id}`,
          inputValidator: (v) => {
            const t = (v || '').trim();
            if (!t) return '会话名称不能为空';
            if (t.length > 80) return '不能超过 80 个字符';
            return true;
          },
          confirmButtonText: '保存',
          cancelButtonText: '取消'
        }
      );
      const title = (value || '').trim();
      if (!title || title === (s.title || '')) return;
      emit('rename', s.id, title);
    } catch {
      // 用户取消
    }
  }
  // 仅用于消除未使用警告（ElMessage 在父级使用，这里保留导入符合一致性）
  void ElMessage;

  function formatRelative(s?: string): string {
    if (!s) return '';
    const t = new Date(s.replace(/-/g, '/')).getTime();
    if (!t) return s;
    const diff = Date.now() - t;
    if (diff < 60_000) return '刚刚';
    if (diff < 3600_000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400_000) return `${Math.floor(diff / 3600_000)}小时前`;
    return s.slice(5, 16);
  }
</script>

<style lang="scss" scoped>
  .ai-session-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    &__header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px 4px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }

  .ai-session-item {
    position: relative;
    padding: 8px 56px 8px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s;
    &:hover {
      background-color: var(--el-fill-color-light);
      .ai-session-item__actions {
        opacity: 1;
      }
    }
    &.is-active {
      background-color: var(--el-color-primary-light-9);
    }
    &__title {
      font-size: 13px;
      color: var(--el-text-color-primary);
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
    &__meta {
      margin-top: 2px;
      font-size: 11px;
      color: var(--el-text-color-secondary);
      display: flex;
      gap: 6px;
      justify-content: space-between;
    }
    &__actions {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      display: flex;
      gap: 6px;
      opacity: 0;
      transition: opacity 0.15s;
    }
    &__action {
      color: var(--el-text-color-secondary);
      cursor: pointer;
      &:hover {
        color: var(--el-color-primary);
      }
      &--danger:hover {
        color: var(--el-color-danger);
      }
    }
  }
</style>
