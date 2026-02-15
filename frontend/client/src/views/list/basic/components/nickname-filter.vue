<!-- 表头筛选框 -->
<template>
  <div @click.stop="">
    <ele-popover
      :width="180"
      trigger="click"
      placement="bottom-end"
      :content-style="{ padding: '12px' }"
      :popper-options="{
        modifiers: [{ name: 'offset', options: { offset: [24, 4] } }]
      }"
    >
      <template #reference>
        <ele-text
          :type="isFiltered ? 'primary' : 'placeholder'"
          :icon="SearchOutlined"
          class="demo-filter-icon"
        />
      </template>
      <div style="margin-bottom: 12px">
        <el-input
          size="small"
          v-model="nickname"
          placeholder="请输入关键字"
          @change="handleSearch"
        />
      </div>
      <div style="text-align: right">
        <el-button size="small" @click="handleReset">重置</el-button>
        <el-button
          size="small"
          type="primary"
          :icon="SearchOutlined"
          class="ele-btn-icon"
          @click="handleSearch"
        >
          搜索
        </el-button>
      </div>
    </ele-popover>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { SearchOutlined } from '@/components/icons';

  const emit = defineEmits<{
    (e: 'search', nickname: string): void;
  }>();

  /** 值 */
  const nickname = ref('');

  /** 是否已筛选 */
  const isFiltered = ref(false);

  /** 搜索 */
  const handleSearch = () => {
    isFiltered.value = !!nickname.value;
    emit('search', nickname.value);
  };

  /**  重置 */
  const handleReset = () => {
    nickname.value = '';
    isFiltered.value = false;
    handleSearch();
  };
</script>

<style lang="scss" scoped>
  .demo-filter-icon {
    line-height: 1;
    cursor: pointer;
    font-size: 13px;
    padding: 4px 2px;
    border-radius: var(--ele-table-icon-radius);
    transition: (color 0.2s, background-color 0.2s);

    :deep(.el-icon > svg) {
      stroke-width: 5;
    }

    &:hover {
      color: var(--ele-table-icon-hover-color);
      background: var(--ele-table-icon-hover-bg);
    }
  }

  @media print {
    .demo-filter-icon {
      display: none;
    }
  }
</style>
