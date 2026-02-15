<template>
  <div ref="editorRef"></div>
</template>

<script lang="ts" setup>
  import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
  import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';

  const props = defineProps<{
    /** v-model */
    modelValue?: string;
    /** 语言 */
    language: string;
    /** 主题 */
    theme?: string;
    /** 原始内容 */
    original?: string;
    /** 原始内容语言 */
    originalLanguage?: string;
    /** 配置 */
    config?: monaco.editor.IStandaloneDiffEditorConstructionOptions;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: string): void;
    (e: 'update:original', original?: string): void;
  }>();

  /** 编辑器实例 */
  let editorIns: monaco.editor.IStandaloneDiffEditor | null = null;
  /** 内容模型 */
  let modifiedModel: monaco.editor.ITextModel | null = null;
  /** 原始内容模型 */
  let originalModel: monaco.editor.ITextModel | null = null;

  /** 编辑器节点 */
  const editorRef = ref<HTMLElement | null>(null);

  /** 更新modelValue */
  const updateModelValue = (value?: string) => {
    emit('update:modelValue', value);
  };

  /** 更新original */
  const updateOriginal = (original?: string) => {
    emit('update:original', original);
  };

  /** 渲染编辑器 */
  const render = () => {
    if (!editorRef.value) {
      return;
    }
    editorIns = monaco.editor.createDiffEditor(editorRef.value, {
      theme: props.theme,
      automaticLayout: true,
      ...(props.config || {})
    });
    if (modifiedModel == null) {
      modifiedModel = monaco.editor.createModel(
        props.modelValue || '',
        props.language
      );
      modifiedModel.onDidChangeContent(() => {
        updateModelValue(modifiedModel?.getValue?.());
      });
    }
    if (originalModel == null) {
      originalModel = monaco.editor.createModel(
        props.original || '',
        props.originalLanguage || props.language
      );
      originalModel.onDidChangeContent(() => {
        updateOriginal(originalModel?.getValue?.());
      });
    }
    editorIns.setModel({
      original: originalModel,
      modified: modifiedModel
    });
  };

  /** 销毁编辑器 */
  const destory = () => {
    if (editorIns != null) {
      editorIns.dispose();
      editorIns = null;
    }
  };

  /** 销毁模型 */
  const destoryModel = () => {
    if (modifiedModel != null) {
      modifiedModel.dispose();
      modifiedModel = null;
    }
    if (originalModel != null) {
      originalModel.dispose();
      originalModel = null;
    }
  };

  /** 获取编辑器实例 */
  const getEditorIns = () => {
    return editorIns;
  };

  /** 更新代码语言和编辑器内容 */
  watch(
    [
      () => props.modelValue,
      () => props.language,
      () => props.original,
      () => props.originalLanguage
    ],
    () => {
      if (
        modifiedModel == null ||
        originalModel == null ||
        modifiedModel.getLanguageId() !== props.language ||
        originalModel.getLanguageId() !== props.originalLanguage
      ) {
        destoryModel();
        destory();
        nextTick(() => {
          render();
        });
        return;
      }
      const content = props.modelValue || '';
      if (content !== modifiedModel.getValue()) {
        modifiedModel.setValue(content);
      }
      const originalContent = props.original || '';
      if (originalContent !== originalModel.getValue()) {
        originalModel.setValue(originalContent);
      }
    }
  );

  /** 更新主题和配置 */
  watch(
    [() => props.theme, () => props.config],
    () => {
      destory();
      nextTick(() => {
        render();
      });
    },
    { deep: true }
  );

  onMounted(() => {
    render();
  });

  onBeforeUnmount(() => {
    destory();
  });

  defineExpose({ getEditorIns });
</script>
