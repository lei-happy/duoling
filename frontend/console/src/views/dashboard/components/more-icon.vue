<template>
  <ele-dropdown
    :items="[
      {
        title: '刷新内容',
        command: 'refresh',
        icon: ReloadOutlined
      },
      {
        title: '编辑卡片',
        command: 'edit',
        icon: EditOutlined
      },
      {
        title: '删除卡片',
        command: 'remove',
        icon: DeleteOutlined,
        danger: true,
        divided: true
      }
    ]"
    :icon-props="{ size: 15 }"
    placement="bottom-end"
    style="cursor: pointer"
    :popper-options="{
      strategy: 'fixed',
      modifiers: [{ name: 'offset', options: { offset: [12, 12] } }]
    }"
    @command="handleCommand"
    class="demo-more-icon"
  >
    <el-icon style="outline: none">
      <MoreOutlined style="transform: scale(1.1)" />
    </el-icon>
  </ele-dropdown>
</template>

<script lang="ts" setup>
  import {
    MoreOutlined,
    ReloadOutlined,
    EditOutlined,
    DeleteOutlined
  } from '@/components/icons';
  import type { Command } from '../model';

  const emit = defineEmits<{
    (e: 'command', command: Command): void;
  }>();

  const handleCommand = (command: Command) => {
    emit('command', command);
  };
</script>

<style lang="scss" scoped>
  .demo-more-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--el-text-color-placeholder);
    font-size: 14px;
    border-radius: 6px;
    margin: 0 -10px 0 0;
    transition: all 0.2s;

    & > .el-icon {
      width: 26px;
      height: 26px;
    }

    &:hover {
      color: var(--el-text-color-regular);
      background: var(--el-fill-color-light);
    }
  }
</style>
