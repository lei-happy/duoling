<!--
  工作台运输线路单元格：完整地点链单行展示，超出省略，悬停看省/市/区全称。
-->
<template>
  <div class="wb-route-cell" :title="fullTitle || undefined">
    {{ lineText }}
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import {
    formatRouteNodesTitle,
    formatRouteTitle,
    shortRegionPath
  } from '@/utils/region-display';

  const props = defineProps<{
    nodes?: string[] | null;
    origin?: string | null;
    destination?: string | null;
    segmentCount?: number | null;
  }>();

  const displayNodes = computed(() => {
    const fromApi = (props.nodes ?? [])
      .map((n) => (n ?? '').trim())
      .filter(Boolean);
    if (fromApi.length >= 2) return fromApi;
    const fallback = [props.origin, props.destination]
      .map((n) => (n ?? '').trim())
      .filter(Boolean);
    return fallback.length ? fallback : ['--'];
  });

  const lineText = computed(() =>
    displayNodes.value.map((n) => shortRegionPath(n)).join(' → ')
  );

  const fullTitle = computed(() => {
    const fromApi = formatRouteNodesTitle(props.nodes);
    if (fromApi) return fromApi;
    return formatRouteTitle(props.origin, props.destination);
  });
</script>

<style lang="scss" scoped>
  .wb-route-cell {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
