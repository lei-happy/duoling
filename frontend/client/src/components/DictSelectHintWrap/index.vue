<template>
  <div class="dict-select-hint-wrap">
    <div class="dict-select-hint-wrap__control">
      <slot />
    </div>
    <el-tooltip placement="top" :show-after="300" :content="tooltipText">
      <el-icon
        class="dict-select-hint-wrap__icon"
        :size="16"
        tabindex="-1"
      >
        <QuestionFilled />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { QuestionFilled } from '@element-plus/icons-vue';

  const props = defineProps<{
    /** 与「系统管理 → 数据字典」左侧字典名称一致，如：性别、机构类型、车辆类型、挂车类型 */
    dictName: string;
  }>();

  const tooltipText = computed(
    () =>
      `若下拉选项不满足需要，可前往「企业管理 → 数据字典」，在「${props.dictName}」中新增或编辑选项。`
  );
</script>

<style scoped>
  .dict-select-hint-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
  }

  .dict-select-hint-wrap__control {
    flex: 1;
    min-width: 0;
  }

  .dict-select-hint-wrap__icon {
    flex-shrink: 0;
    color: var(--el-text-color-secondary);
    cursor: help;
    outline: none;
  }

  .dict-select-hint-wrap__icon:hover {
    color: var(--el-color-primary);
  }
</style>
