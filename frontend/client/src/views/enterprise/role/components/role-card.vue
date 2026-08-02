<!-- 角色画廊单卡 -->
<template>
  <article class="role-card">
    <header class="role-card__header">
      <h3 class="role-card__name" :title="data.roleName">
        {{ data.roleName || '—' }}
      </h3>
    </header>

    <el-tooltip
      placement="top"
      :disabled="!showDescTooltip"
      :show-after="300"
      popper-class="role-card-desc-tooltip"
    >
      <template #content>
        <div class="role-card-desc-tooltip__body">{{ descText }}</div>
      </template>
      <p ref="descRef" class="role-card__desc">{{ descText }}</p>
    </el-tooltip>

    <div class="role-card__stats">
      <button
        type="button"
        class="role-card__users-btn"
        :disabled="!(data.userCount ?? 0)"
        :title="(data.userCount ?? 0) ? '查看人员' : undefined"
        @click.stop="emit('viewUsers')"
      >
        {{ data.userCount ?? 0 }} 人
      </button>
      <span class="role-card__stats-sep">·</span>
      <span>{{ data.menuCount ?? 0 }} 项权限</span>
    </div>

    <footer class="role-card__footer">
      <el-button type="primary" @click="emit('auth')">权限管理</el-button>
      <div class="role-card__secondary">
        <el-button text type="primary" @click="emit('edit')">编辑</el-button>
        <el-button text type="danger" @click="emit('delete')">删除</el-button>
      </div>
    </footer>
  </article>
</template>

<script lang="ts" setup>
  import { computed, nextTick, onMounted, ref, watch } from 'vue';
  import type { Role } from '@/api/system/role/model';

  const props = defineProps<{
    data: Role;
  }>();

  const emit = defineEmits<{
    (e: 'auth'): void;
    (e: 'edit'): void;
    (e: 'delete'): void;
    (e: 'viewUsers'): void;
  }>();

  const descRef = ref<HTMLElement | null>(null);
  const showDescTooltip = ref(false);

  const descText = computed(() =>
    props.data.comments?.trim() ? props.data.comments : '暂无描述'
  );

  const updateDescOverflow = () => {
    nextTick(() => {
      const el = descRef.value;
      if (!el || !props.data.comments?.trim()) {
        showDescTooltip.value = false;
        return;
      }
      showDescTooltip.value = el.scrollHeight > el.clientHeight + 1;
    });
  };

  onMounted(updateDescOverflow);
  watch(descText, updateDescOverflow);
</script>

<style scoped>
  .role-card {
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 180px;
    padding: 16px 16px 14px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background: var(--el-bg-color);
    box-sizing: border-box;
    transition:
      border-color 0.15s ease,
      box-shadow 0.15s ease;
  }

  .role-card:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
  }

  .role-card__header {
    min-width: 0;
  }

  .role-card__name {
    margin: 0;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.35;
    color: var(--el-text-color-primary);
  }

  .role-card__desc {
    margin: 0;
    flex: 1;
    min-height: calc(1.5em * 2);
    max-height: calc(1.5em * 5);
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 5;
    line-clamp: 5;
    overflow: hidden;
    font-size: 13px;
    line-height: 1.5;
    color: var(--el-text-color-secondary);
    cursor: default;
  }

  .role-card__stats {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    font-variant-numeric: tabular-nums;
  }

  .role-card__users-btn {
    margin: 0;
    padding: 0;
    border: none;
    background: transparent;
    color: var(--el-color-primary);
    font: inherit;
    font-variant-numeric: tabular-nums;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 2px;
  }

  .role-card__users-btn:hover:not(:disabled) {
    color: var(--el-color-primary-light-3);
  }

  .role-card__users-btn:disabled {
    color: var(--el-text-color-regular);
    cursor: default;
    text-decoration: none;
  }

  .role-card__stats-sep {
    color: var(--el-text-color-placeholder);
  }

  .role-card__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding-top: 4px;
    margin-top: auto;
  }

  .role-card__secondary {
    display: flex;
    align-items: center;
    gap: 0 2px;
  }
</style>

<!-- tooltip 挂载到 body，需非 scoped -->
<style>
  .role-card-desc-tooltip.el-popper {
    max-width: 320px !important;
  }

  .role-card-desc-tooltip__body {
    max-width: 300px;
    max-height: 200px;
    overflow: auto;
    white-space: normal;
    word-break: break-word;
    overflow-wrap: anywhere;
    line-height: 1.5;
    font-size: 13px;
  }
</style>
