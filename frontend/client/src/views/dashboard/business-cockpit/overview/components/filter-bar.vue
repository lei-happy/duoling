<!-- 经营驾驶舱 - 顶部时间筛选条 -->
<template>
  <ele-card class="filter-bar" :body-style="{ padding: '12px 22px' }">
    <div class="filter-bar-inner">
      <div class="filter-bar-title">
        <ele-text size="xl" type="primary">经营总览</ele-text>
        <ele-text type="placeholder" size="sm" style="margin-left: 8px">
          数据时间：{{ formatRange }}
        </ele-text>
      </div>
      <div class="filter-bar-right">
        <el-radio-group v-model="presetVal" @change="handlePresetChange">
          <el-radio-button value="1" label="今天" />
          <el-radio-button value="2" label="本周" />
          <el-radio-button value="3" label="本月" />
          <el-radio-button value="4" label="本年" />
        </el-radio-group>
        <div class="filter-bar-date">
          <el-date-picker
            unlink-panels
            type="datetimerange"
            v-model="datetime"
            range-separator="-"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            class="ele-fluid"
            @change="handleDateChange"
          />
        </div>
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import {
    useCockpitFilter,
    type DatePreset
  } from '../composables/use-cockpit-filter';

  const { state, setPreset, setRange } = useCockpitFilter();

  const presetVal = ref<DatePreset>(state.preset);
  const datetime = ref<[string, string]>([state.start, state.end]);

  watch(
    () => [state.start, state.end, state.preset] as const,
    ([s, e, p]) => {
      presetVal.value = p as DatePreset;
      datetime.value = [s, e];
    }
  );

  const formatRange = computed(() => {
    return `${state.start.slice(0, 16)} ~ ${state.end.slice(0, 16)}`;
  });

  const handlePresetChange = (value: string | number | boolean | undefined) => {
    const v = String(value) as DatePreset;
    setPreset(v);
  };

  const handleDateChange = (val: [string, string] | null) => {
    if (!val) return;
    setRange(val[0], val[1], 'custom');
  };
</script>

<style lang="scss" scoped>
  .filter-bar {
    margin-bottom: 16px;

    .filter-bar-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }

    .filter-bar-title {
      display: flex;
      align-items: baseline;
    }

    .filter-bar-right {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .filter-bar-date {
      width: 320px;
    }
  }
</style>
