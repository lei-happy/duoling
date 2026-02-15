<!-- 增删改查构建器 -->
<template>
  <EleCrudBuilder
    v-bind="{ ...emitProps, ...$props }"
    :templateData="templateData || defaultTemplateData"
    :pageConfigFormItems="pageConfigFormItems || defaultPageConfigFormItems"
    :fieldEditFormItems="fieldEditFormItems || defaultFieldEditFormItems"
    :crudComponent="crudComponent || ProCrud"
    :proFormComponent="proFormComponent || ProForm"
    :proFormBuilderComponent="proFormBuilderComponent || ProFormBuilder"
    :codeEditerComponent="codeEditerComponent || CodeEditer"
    :jsonEditerComponent="jsonEditerComponent || JsonEditer"
    :codeViewerComponent="codeViewerComponent || CodeViewer"
    :headerTools="headerTools ?? defaultHeaderRightTools"
  >
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleCrudBuilder>
</template>

<script lang="ts" setup>
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import type { HeaderRightToolName } from 'ele-admin-plus/es/ele-crud-builder/types';
  import {
    crudBuilderProps,
    crudBuilderEmits
  } from 'ele-admin-plus/es/ele-crud-builder/props';
  import {
    defaultPageConfigFormItems,
    defaultFieldEditFormItems
  } from 'ele-admin-plus/es/ele-crud-builder/util';
  import ProCrud from '@/components/ProCrud/index.vue';
  import ProForm from '@/components/ProForm/index.vue';
  import ProFormBuilder from '@/components/ProFormBuilder/index.vue';
  import CodeEditer from '@/components/ProFormBuilder/components/code-editer.vue';
  import JsonEditer from '@/components/ProFormBuilder/components/json-editer.vue';
  import CodeViewer from '@/components/CodeViewer/index.vue';
  import { defaultTemplateData } from './components/template-data';

  defineOptions({ name: 'ProCrudBuilder' });

  defineProps(crudBuilderProps);

  const emit = defineEmits(crudBuilderEmits);

  const { emitProps } = useComponentEvents(crudBuilderEmits, emit);

  /** 顶栏右侧按钮布局 */
  const defaultHeaderRightTools: HeaderRightToolName[] = [
    'import',
    'export',
    'clear',
    'code'
  ];
</script>
