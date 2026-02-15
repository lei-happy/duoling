<!-- 配置式增删改查 -->
<template>
  <EleCrud
    v-bind="{ ...emitProps, ...$props }"
    ref="crudRef"
    :httpRequest="request"
    :proFormComponent="proFormComponent || ProForm"
  >
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleCrud>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import {
    useComponentEvents,
    useComponentExpose
  } from 'ele-admin-plus/es/utils/hook';
  import type { EleCrudInstance } from 'ele-admin-plus/es/ele-app/plusx';
  import { crudProps, crudEmits } from 'ele-admin-plus/es/ele-crud/props';
  import ProForm from '@/components/ProForm/index.vue';
  import request from '@/utils/request';

  defineOptions({ name: 'ProCrud' });

  defineProps(crudProps);

  const emit = defineEmits(crudEmits);

  const { emitProps } = useComponentEvents(crudEmits, emit);

  /** 增删改查组件 */
  const crudRef = ref<EleCrudInstance>(null);

  const exposeValues = useComponentExpose(
    crudRef,
    ['getTableSelections'],
    ['tableRef']
  );

  defineExpose({ ...exposeValues, crudRef });
</script>
