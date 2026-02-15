<!-- markdown 编辑器 -->
<template>
  <div ref="rootRef" class="ele-bytemd-wrap"></div>
</template>

<script lang="ts" setup>
  import { ref, watch, onMounted } from 'vue';
  import { Editor } from 'bytemd';
  import type { BytemdPlugin, BytemdLocale, ViewerProps } from 'bytemd';
  import 'bytemd/dist/index.min.css';

  defineOptions({ name: 'ByteMdEditor' });

  interface EditorConfig {
    plugins?: BytemdPlugin[];
    sanitize?: (schema: any) => any;
    remarkRehype?: Record<any, any>;
    mode?: 'split' | 'tab' | 'auto';
    previewDebounce?: number;
    placeholder?: string;
    editorConfig?: Record<any, any>;
    locale?: Partial<BytemdLocale>;
    uploadImages?: (
      files: File[]
    ) => Promise<Pick<any, 'url' | 'alt' | 'title'>[]>;
    overridePreview?: (el: HTMLElement, props: ViewerProps) => void;
    maxLength?: number;
  }

  const props = withDefaults(
    defineProps<{
      /** 绑定值 */
      modelValue: string;
      /** 编辑器配置 */
      config?: EditorConfig;
      /** 高度 */
      height?: string;
      /** 全屏时的层级 */
      fullIndex?: number;
    }>(),
    {
      fullIndex: 999
    }
  );

  const emit = defineEmits<{
    (e: 'update:modelValue', value?: string): void;
    (e: 'change', value?: string): void;
  }>();

  /** 编辑器实例 */
  let editor: InstanceType<typeof Editor> | null = null;

  /** 根节点 */
  const rootRef = ref<HTMLElement | null>(null);

  // 渲染编辑器
  onMounted(() => {
    // @ts-ignore
    const ins = new Editor({
      target: rootRef.value as HTMLElement,
      props: Object.assign({}, props.config, { value: props.modelValue })
    });
    // @ts-ignore
    ins.$on('change', (e: any) => {
      emit('update:modelValue', e.detail.value);
      emit('change', e.detail.value);
    });
    editor = ins;
  });

  // 更新配置
  watch(
    () => props.config,
    (config) => {
      const option = Object.assign({}, config);
      Object.keys(option).forEach((key) => {
        if (typeof option[key] === 'undefined') {
          delete option[key];
        }
      });
      // @ts-ignore
      editor?.$set?.(option);
    },
    { deep: true }
  );

  watch(
    () => props.modelValue,
    (value) => {
      // @ts-ignore
      editor?.$set?.({ value });
    }
  );

  defineExpose({ editor });
</script>

<style lang="scss">
  @use 'element-plus/theme-chalk/src/mixins/function.scss' as *;

  .ele-bytemd-wrap {
    width: 100%;
    line-height: initial;

    /* 修改编辑器高度 */
    .bytemd {
      height: v-bind(height);
      /* background: none; */

      /* .CodeMirror {
        background: none;
      } */

      /* 修改全屏的zIndex */
      &.bytemd-fullscreen {
        z-index: v-bind(fullIndex);
        /* background: getCssVar('bg-color'); */
      }

      /* 去掉默认的最大宽度限制 */
      .CodeMirror .CodeMirror-lines {
        max-width: 100%;
      }

      pre.CodeMirror-line,
      pre.CodeMirror-line-like {
        padding: 0 24px;
      }

      .markdown-body {
        max-width: 100%;
        padding: 16px 24px;
      }

      /* 去掉github图标 */
      .bytemd-toolbar-right > .bytemd-toolbar-icon:last-child {
        display: none;
      }
    }
  }

  /* body .markdown-body {
    background: none;
  } */
</style>
