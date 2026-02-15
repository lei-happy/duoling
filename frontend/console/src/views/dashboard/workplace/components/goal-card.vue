<!-- 本月目标 -->
<template>
  <ele-card :header="title" :body-style="{ height: '370px' }">
    <template #extra>
      <more-icon @command="handleCommand" />
    </template>
    <div class="workplace-goal">
      <el-progress
        :width="180"
        :percentage="80"
        color="var(--el-color-primary)"
        type="dashboard"
        :format="() => ''"
      />
      <div class="workplace-goal-body">
        <el-tag
          size="large"
          :disable-transitions="true"
          style="width: 36px; height: 36px; border-radius: 50%; line-height: 0"
        >
          <el-icon style="cursor: default; border-radius: 0">
            <TrophyBase />
          </el-icon>
        </el-tag>
        <div style="font-size: 40px">285</div>
      </div>
      <div>恭喜, 本月目标已达标!</div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { TrophyBase } from '@element-plus/icons-vue';
  import MoreIcon from './more-icon.vue';
  import type { Command } from '../model';

  defineProps<{
    title?: string;
  }>();

  const emit = defineEmits<{
    (e: 'command', command: Command): void;
  }>();

  const handleCommand = (command: Command) => {
    emit('command', command);
  };
</script>

<style lang="scss" scoped>
  .workplace-goal {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;

    .workplace-goal-body {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 180px;
      margin: -48px 0 0 -90px;
      text-align: center;
    }
  }
</style>
