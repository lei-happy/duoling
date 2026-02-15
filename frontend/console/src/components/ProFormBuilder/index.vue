<!-- 表单构建器 -->
<template>
  <EleProFormBuilder
    v-bind="{ ...emitProps, ...$props }"
    :componentData="componentData || defaultComponentData"
    :templateData="templateData || defaultTemplateData"
    :configFormItems="configFormItems || defaultConfigFormItems"
    :configFormPresetProps="configFormPresetProps || formPresetProps"
    :proFormComponent="proFormComponent || ProForm"
    :codeEditerComponent="codeEditerComponent || CodeEditer"
    :jsonEditerComponent="jsonEditerComponent || JsonEditer"
    :htmlEditerComponent="htmlEditerComponent || HtmlEditer"
    :codeViewerComponent="codeViewerComponent || CodeViewer"
    :headerTools="headerTools ?? defaultHeaderRightTools"
    :proFormInitialProps="{ footer: true }"
  >
    <template
      v-if="!$slots.proFormBuilderIconInput"
      #proFormBuilderIconInput="{ item, modelValue, updateValue }"
    >
      <IconEditer
        v-bind="item.props || {}"
        :modelValue="modelValue"
        @update:modelValue="updateValue"
      />
    </template>
    <template v-for="name in Object.keys($slots)" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleProFormBuilder>
</template>

<script lang="ts" setup>
  import { useComponentEvents } from 'ele-admin-plus/es/utils/hook';
  import type { HeaderRightToolName } from 'ele-admin-plus/es/ele-pro-form-builder/types';
  import {
    proFormBuilderProps,
    proFormBuilderEmits
  } from 'ele-admin-plus/es/ele-pro-form-builder/props';
  import {
    defaultConfigFormItems,
    defaultConfigFormPresetProps as formPresetProps
  } from 'ele-admin-plus/es/ele-pro-form-builder/util';
  import ProForm from '@/components/ProForm/index.vue';
  import CodeViewer from '@/components/CodeViewer/index.vue';
  import { defaultComponentData } from './components/component-data';
  import { defaultTemplateData } from './components/template-data';
  import CodeEditer from './components/code-editer.vue';
  import JsonEditer from './components/json-editer.vue';
  import HtmlEditer from './components/html-editer.vue';
  import IconEditer from './components/icon-editer.vue';

  defineOptions({ name: 'ProFormBuilder' });

  defineProps(proFormBuilderProps);

  const emit = defineEmits(proFormBuilderEmits);

  const { emitProps } = useComponentEvents(proFormBuilderEmits, emit);

  /** 顶栏右侧按钮布局 */
  const defaultHeaderRightTools: HeaderRightToolName[] = [
    'import',
    'export',
    'clear',
    'preview',
    'code'
  ];
</script>
