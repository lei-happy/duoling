<!--
  工作台运输线路单元格：市/区 → 市/区，悬停看完整省/市/区。
-->
<template>
  <div class="wb-route-cell" :title="fullTitle || undefined">
    <span class="wb-route-cell__side">{{ shortOrigin }}</span>
    <el-icon class="wb-route-cell__arrow"><Right /></el-icon>
    <span class="wb-route-cell__side">{{ shortDest }}</span>
    <el-tag
      v-if="segmentCount > 1"
      size="small"
      type="info"
      effect="plain"
      class="wb-route-cell__seg"
    >
      {{ segmentCount }} 段
    </el-tag>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { Right } from '@element-plus/icons-vue';
  import { formatRouteTitle, shortRegionPath } from '@/utils/region-display';

  const props = defineProps<{
    origin?: string | null;
    destination?: string | null;
    segmentCount?: number | null;
  }>();

  const shortOrigin = computed(() => shortRegionPath(props.origin));
  const shortDest = computed(() => shortRegionPath(props.destination));
  const fullTitle = computed(() =>
    formatRouteTitle(props.origin, props.destination)
  );
  const segmentCount = computed(() => props.segmentCount ?? 0);
</script>

<style lang="scss" scoped>
  .wb-route-cell {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    min-width: 0;

    &__side {
      min-width: 0;
      flex: 1 1 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    &__arrow {
      flex-shrink: 0;
      margin: 0 6px;
    }

    &__seg {
      flex-shrink: 0;
      margin-left: 6px;
    }
  }
</style>
