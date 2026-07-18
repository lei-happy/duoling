<template>
  <div class="overview-grid">
    <div
      v-for="card in cards"
      :key="card.path"
      class="overview-grid__card"
      @click="emit('navigate', card.path)"
    >
      <div class="overview-grid__icon">
        <overview-icon :name="card.icon" />
      </div>
      <div class="overview-grid__body">
        <div class="overview-grid__title">
          {{ card.title }}
          <el-icon class="overview-grid__arrow"><ArrowRight /></el-icon>
        </div>
        <div v-if="card.desc" class="overview-grid__desc">{{ card.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ArrowRight } from '@element-plus/icons-vue';
  import type { OverviewModuleCard } from '@/config/module-overview/types';
  import OverviewIcon from './overview-icon.vue';

  defineOptions({ name: 'OverviewModuleGrid' });

  defineProps<{
    cards: OverviewModuleCard[];
  }>();

  const emit = defineEmits<{
    (e: 'navigate', path: string): void;
  }>();
</script>

<style lang="scss" scoped>
  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 12px;
  }

  .overview-grid__card {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
    cursor: pointer;
    transition:
      border-color 0.2s,
      box-shadow 0.2s,
      transform 0.2s;

    &:hover {
      border-color: var(--el-color-primary-light-5);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
      transform: translateY(-2px);

      .overview-grid__arrow {
        opacity: 1;
        transform: translateX(2px);
      }
    }
  }

  .overview-grid__icon {
    flex: 0 0 auto;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .overview-grid__body {
    min-width: 0;
  }

  .overview-grid__title {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 15px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .overview-grid__arrow {
    font-size: 14px;
    color: var(--el-color-primary);
    opacity: 0;
    transition:
      opacity 0.2s,
      transform 0.2s;
  }

  .overview-grid__desc {
    margin-top: 6px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }
</style>
