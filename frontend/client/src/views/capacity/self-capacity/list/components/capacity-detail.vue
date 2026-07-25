<template>
  <div class="capacity-detail">
    <div class="capacity-detail__header">
      <h3 class="capacity-detail__title">
        运力详情 - {{ data?.driverName || '' }}
      </h3>
    </div>
    <div class="capacity-detail__body">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="运力信息" name="info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="驾驶员姓名">{{
              data?.driverName || '—'
            }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{
              data?.driverPhone || '—'
            }}</el-descriptions-item>
            <el-descriptions-item label="所属部门">{{
              data?.departmentName || '—'
            }}</el-descriptions-item>
            <el-descriptions-item label="绑定时间">{{
              data?.boundAt || '—'
            }}</el-descriptions-item>
            <el-descriptions-item label="主车牌">{{
              data?.plateNumber || '—'
            }}</el-descriptions-item>
            <el-descriptions-item label="挂车牌">{{
              data?.trailerPlateNumber || '—'
            }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="车辆历史" name="vehicle">
          <el-empty description="暂无车辆历史数据" />
        </el-tab-pane>
        <el-tab-pane label="驾驶员历史" name="driver">
          <el-empty description="暂无驾驶员历史数据" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';

  const props = defineProps<{
    data: Capacity | null;
  }>();

  const activeTab = ref('info');

  watch(
    () => props.data,
    (val) => {
      if (val) {
        activeTab.value = 'info';
      }
    }
  );
</script>

<style scoped>
  .capacity-detail {
    display: flex;
    flex-direction: column;
    max-height: 86vh;
  }

  .capacity-detail__header {
    flex-shrink: 0;
    padding: 20px 48px 16px 24px;
    border-bottom: 1px solid var(--el-border-color-extra-light);
  }

  .capacity-detail__title {
    margin: 0;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .capacity-detail__body {
    flex: 1;
    min-height: 300px;
    padding: 18px 24px 24px;
    overflow: auto;
  }
</style>
