<template>
  <div class="ai-employee-list">
    <div class="ai-employee-list__header">选择数字员工</div>
    <div
      v-for="emp in employees"
      :key="emp.code"
      class="ai-employee-card"
      :class="{ 'is-active': emp.code === modelValue }"
      @click="$emit('update:modelValue', emp.code)"
    >
      <div class="ai-employee-card__avatar">
        <el-avatar :size="36" :src="normalizeAvatar(emp.avatar)">
          {{ (emp.name || '').slice(0, 1) }}
        </el-avatar>
      </div>
      <div class="ai-employee-card__body">
        <div class="ai-employee-card__name">{{ emp.name }}</div>
        <div class="ai-employee-card__desc">
          {{ emp.description || empTypeText(emp.employeeType) }}
        </div>
      </div>
    </div>
    <ele-text v-if="!employees.length" type="placeholder" style="padding: 12px">
      暂无可用数字员工，请联系运营在「AI 数字员工」中创建
    </ele-text>
  </div>
</template>

<script lang="ts" setup>
  import type { AiEmployee } from '@/api/ai/model';

  defineProps<{
    employees: AiEmployee[];
    modelValue?: string;
  }>();
  defineEmits<{ (e: 'update:modelValue', code: string): void }>();

  function normalizeAvatar(p?: string): string | undefined {
    const s = (p || '').trim();
    if (!s) return undefined;
    if (
      s.startsWith('http://') ||
      s.startsWith('https://') ||
      s.startsWith('data:')
    ) {
      return s;
    }
    return s.startsWith('/') ? s : `/${s}`;
  }

  function empTypeText(t?: string): string {
    switch (t) {
      case 'form_recorder':
        return '录单员';
      case 'data_analyst':
        return '数据分析员';
      case 'archivist':
        return '档案管理员';
      default:
        return '数字员工';
    }
  }
</script>

<style lang="scss" scoped>
  .ai-employee-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    &__header {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      padding: 8px 12px 4px;
    }
  }

  .ai-employee-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.15s;
    &:hover {
      background-color: var(--el-fill-color-light);
    }
    &.is-active {
      background-color: var(--el-color-primary-light-9);
      box-shadow: inset 2px 0 0 0 var(--el-color-primary);
    }
    &__body {
      flex: 1;
      min-width: 0;
    }
    &__name {
      font-size: 13px;
      color: var(--el-text-color-primary);
      font-weight: 500;
    }
    &__desc {
      margin-top: 2px;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
    }
  }
</style>
