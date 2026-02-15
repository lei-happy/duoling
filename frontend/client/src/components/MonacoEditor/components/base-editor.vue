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
    /** 配置 */
    config?: monaco.editor.IStandaloneEditorConstructionOptions;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: string): void;
  }>();

  /** 编辑器实例 */
  let editorIns: monaco.editor.IStandaloneCodeEditor | null = null;

  /** 编辑器节点 */
  const editorRef = ref<HTMLElement | null>(null);

  /** 更新modelValue */
  const updateModelValue = (value?: string) => {
    emit('update:modelValue', value);
  };

  /** 渲染编辑器 */
  const render = () => {
    if (!editorRef.value) {
      return;
    }
    editorIns = monaco.editor.create(editorRef.value, {
      value: props.modelValue || '',
      language: props.language,
      theme: props.theme,
      automaticLayout: true,
      ...(props.config || {})
    });
    // modelValue属性同步编辑器内容
    editorIns.onDidChangeModelContent(() => {
      updateModelValue(editorIns?.getValue?.());
    });
  };

  /** 销毁编辑器 */
  const destory = () => {
    if (editorIns != null) {
      editorIns.dispose();
      editorIns = null;
    }
  };

  /** 修改内容 */
  const setContent = (value: string) => {
    if (editorIns && value !== editorIns.getValue()) {
      editorIns.setValue(value);
    }
  };

  /** 获取编辑器实例 */
  const getEditorIns = () => {
    return editorIns;
  };

  /** 编辑器内容同步modelValue属性 */
  watch(
    () => props.modelValue,
    (value) => {
      setContent(value || '');
    }
  );

  /** 更新代码语言和编辑器配置 */
  watch(
    [() => props.language, () => props.config],
    () => {
      destory();
      nextTick(() => {
        render();
      });
    },
    { deep: true }
  );

  /** 更新编辑器主题 */
  watch(
    () => props.theme,
    (theme) => {
      editorIns && editorIns.updateOptions({ theme });
    }
  );

  onMounted(() => {
    render();
  });

  onBeforeUnmount(() => {
    destory();
  });

  defineExpose({ getEditorIns });
</script>
