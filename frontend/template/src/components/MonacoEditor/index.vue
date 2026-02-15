<!-- 代码编辑器 -->
<template>
  <DiffEditor
    v-if="diff"
    ref="editorRef"
    v-model="model"
    :language="language"
    :theme="theme"
    v-model:original="original"
    :originalLanguage="originalLanguage"
    :config="config"
    style="height: 600px"
  />
  <BaseEditor
    v-else
    ref="editorRef"
    v-model="model"
    :language="language"
    :theme="theme"
    :config="config"
    style="height: 600px"
  />
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import BaseEditor from './components/base-editor.vue';
  import DiffEditor from './components/diff-editor.vue';
  import type { editor } from 'monaco-editor/esm/vs/editor/editor.api';
  import './user-worker';

  defineOptions({ name: 'MonacoEditor' });

  withDefaults(
    defineProps<{
      /** 语言 */
      language?: string;
      /** 主题 */
      theme?: string;
      /** 是否为diff模式 */
      diff?: boolean;
      /** 原始内容语言 */
      originalLanguage?: string;
      /** 配置 */
      config?:
        | editor.IStandaloneEditorConstructionOptions
        | editor.IStandaloneDiffEditorConstructionOptions;
    }>(),
    { language: 'typescript' }
  );

  /** v-model */
  const model = defineModel({ type: String });

  /** 原始内容 */
  const original = defineModel('original', { type: String });

  /** 组件实例 */
  const editorRef = ref<
    InstanceType<typeof BaseEditor> | InstanceType<typeof DiffEditor> | null
  >(null);

  /** 获取编辑器实例 */
  const getEditorIns = ():
    | editor.IStandaloneCodeEditor
    | editor.IStandaloneDiffEditor
    | null
    | undefined => {
    return editorRef.value?.getEditorIns?.();
  };

  defineExpose({ getEditorIns });
</script>
