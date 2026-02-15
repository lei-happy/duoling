<!-- 富文本编辑器 -->
<template>
  <MonacoEditor
    theme="vs-dark"
    language="html"
    :modelValue="modelValue"
    @update:modelValue="updateModelValue"
    :config="editorConfig"
    :style="{ height: '100%' }"
  />
</template>

<script lang="ts" setup>
  import type { editor } from 'monaco-editor/esm/vs/editor/editor.api';
  import MonacoEditor from '@/components/MonacoEditor/index.vue';
  const editorConfig: editor.IStandaloneEditorConstructionOptions = {
    contextmenu: false,
    minimap: { enabled: false },
    suggest: { enabled: false } as any,
    inlineSuggest: { enabled: false },
    quickSuggestions: false,
    parameterHints: { enabled: false },
    autoClosingBrackets: 'never',
    autoClosingQuotes: 'never',
    formatOnType: false,
    formatOnPaste: false,
    codeLens: false,
    lightbulb: { enabled: 'off' as editor.ShowLightbulbIconMode.Off },
    snippetSuggestions: 'none',
    wordBasedSuggestions: 'off',
    selectionHighlight: false,
    occurrencesHighlight: 'off',
    matchBrackets: 'never'
  };

  defineProps<{
    /** 代码 */
    modelValue?: string;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: string): void;
  }>();

  /** 更新代码 */
  const updateModelValue = (value?: string) => {
    emit('update:modelValue', value);
  };
</script>
