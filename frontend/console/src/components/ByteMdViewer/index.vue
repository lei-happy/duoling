<!-- markdown 解析器 -->
<!-- eslint-disable vue/no-v-html -->
<template>
  <div
    ref="rootRef"
    v-html="content"
    class="markdown-body"
    @click="handleClick"
  >
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
  import type { BytemdPlugin } from 'bytemd';
  import { getProcessor } from 'bytemd';

  defineOptions({ name: 'ByteMdViewer' });

  interface ViewerConfig {
    plugins?: BytemdPlugin[];
    sanitize?: (schema: any) => any;
    remarkRehype?: Record<any, any>;
  }

  const props = defineProps<{
    value: string;
    config?: ViewerConfig;
  }>();

  /** 根节点 */
  const rootRef = ref<HTMLElement | null>(null);

  /** 解析后内容 */
  const content = ref<any | null>(null);

  /** 已绑定的插件 */
  const cbs = ref<(void | (() => void))[]>([]);

  /** 绑定插件 */
  const on = () => {
    if (props.config?.plugins && rootRef.value && content.value) {
      cbs.value = props.config.plugins.map(({ viewerEffect }) => {
        return (
          viewerEffect &&
          viewerEffect({
            markdownBody: rootRef.value as HTMLElement,
            file: content.value
          })
        );
      });
    }
  };

  /** 解绑插件 */
  const off = () => {
    if (cbs.value) {
      cbs.value.forEach((cb) => cb && cb());
    }
  };

  /** 处理点击事件支持锚点 */
  const handleClick = (e: MouseEvent) => {
    const $ = e.target as HTMLElement;
    if ($.tagName !== 'A') {
      return;
    }
    const href = $.getAttribute('href');
    if (!href || !href.startsWith('#')) {
      return;
    }
    const $root = rootRef.value;
    if ($root) {
      const dest = $root.querySelector(`#user-content-${href.slice(1)}`);
      if (dest) {
        dest.scrollIntoView();
      }
    }
  };

  // 解析
  watch(
    [() => props.value, () => props.config],
    () => {
      try {
        content.value = getProcessor(
          Object.assign({}, props.config)
        ).processSync(props.value);
      } catch (e) {
        console.error(e);
      }
      off();
      nextTick(() => {
        on();
      });
    },
    {
      immediate: true,
      deep: true
    }
  );

  onMounted(() => {
    on();
  });

  onBeforeUnmount(() => {
    off();
  });
</script>
