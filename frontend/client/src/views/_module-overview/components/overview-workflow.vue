<template>
  <div class="overview-workflow">
    <template v-for="(step, index) in steps" :key="step.title + index">
      <div
        class="overview-workflow__step"
        :class="{ 'is-clickable': !!step.path }"
        @click="step.path && emit('navigate', step.path)"
      >
        <div class="overview-workflow__badge">
          <overview-icon :name="step.icon" />
          <span class="overview-workflow__index">{{ index + 1 }}</span>
        </div>
        <div class="overview-workflow__title">{{ step.title }}</div>
        <div v-if="step.desc" class="overview-workflow__desc">
          {{ step.desc }}
        </div>
      </div>
      <div
        v-if="index < steps.length - 1"
        class="overview-workflow__arrow"
        aria-hidden="true"
      >
        <el-icon><ArrowRightBold /></el-icon>
      </div>
    </template>
  </div>
</template>

<script lang="ts" setup>
  import { ArrowRightBold } from '@element-plus/icons-vue';
  import type { OverviewWorkflowStep } from '@/config/module-overview/types';
  import OverviewIcon from './overview-icon.vue';

  defineOptions({ name: 'OverviewWorkflow' });

  defineProps<{
    steps: OverviewWorkflowStep[];
  }>();

  const emit = defineEmits<{
    (e: 'navigate', path: string): void;
  }>();
</script>

<style lang="scss" scoped>
  .overview-workflow {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 8px;
  }

  .overview-workflow__step {
    flex: 1 1 0;
    min-width: 120px;
    text-align: center;
    padding: 16px 12px;
    border-radius: 10px;
    border: 1px solid transparent;
    transition:
      background 0.2s,
      border-color 0.2s,
      transform 0.2s;

    &.is-clickable {
      cursor: pointer;

      &:hover {
        background: var(--el-color-primary-light-9);
        border-color: var(--el-color-primary-light-5);
        transform: translateY(-2px);
      }
    }
  }

  .overview-workflow__badge {
    position: relative;
    width: 52px;
    height: 52px;
    margin: 0 auto 12px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .overview-workflow__index {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    font-size: 12px;
    line-height: 20px;
    color: #fff;
    background: var(--el-color-primary);
  }

  .overview-workflow__title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .overview-workflow__desc {
    margin-top: 6px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }

  .overview-workflow__arrow {
    align-self: center;
    padding-top: 26px;
    color: var(--el-text-color-placeholder);
    flex: 0 0 auto;
  }

  @media screen and (max-width: 720px) {
    .overview-workflow__arrow {
      display: none;
    }

    .overview-workflow__step {
      flex-basis: 45%;
    }
  }
</style>
