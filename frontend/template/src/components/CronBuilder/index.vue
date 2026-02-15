<!-- Cron 表达式生成器 -->
<template>
  <EleCronBuilder v-bind="{ ...emitProps, ...$props }">
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleCronBuilder>
</template>

<script lang="ts" setup>
  import {
    cronBuilderProps,
    cronBuilderEmits
  } from 'ele-admin-plus/es/ele-cron-builder/props';
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';

  defineOptions({ name: 'CronBuilder' });

  defineProps(cronBuilderProps);

  const emit = defineEmits(cronBuilderEmits);

  const { emitProps } = useComponentEvents(cronBuilderEmits, emit);
</script>
