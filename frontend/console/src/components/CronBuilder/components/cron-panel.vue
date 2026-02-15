<template>
  <EleCronPanel v-bind="{ ...emitProps, ...$props }">
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleCronPanel>
</template>

<script lang="ts" setup>
  import {
    cronPanelProps,
    cronPanelEmits
  } from 'ele-admin-plus/es/ele-cron-panel/props';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';

  defineProps(cronPanelProps);

  const emit = defineEmits(cronPanelEmits);

  const { emitProps } = useComponentEvents(cronPanelEmits, emit);
</script>
