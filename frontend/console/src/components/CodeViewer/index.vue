<!-- eslint-disable vue/no-v-html -->
<template>
  <div class="ele-code-viewer">
    <div class="ele-code-viewer-line-numbers">
      <div v-for="n in codeLines" :key="n">{{ n }}</div>
    </div>
    <pre v-html="codeHtml"></pre>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import hljs from 'highlight.js';
  import 'highlight.js/styles/github-dark.css';
  import xml from 'highlight.js/lib/languages/xml';
  import java from 'highlight.js/lib/languages/java';
  import sql from 'highlight.js/lib/languages/sql';
  hljs.registerLanguage('vue', xml);
  hljs.registerLanguage('xml', xml);
  hljs.registerLanguage('java', java);
  hljs.registerLanguage('sql', sql);

  defineOptions({ name: 'CodeViewer' });

  const props = defineProps({
    /** 代码内容 */
    code: String,
    /** 代码语言 */
    language: String
  });

  /** 代码行号 */
  const codeLines = ref([1]);

  /** 高亮后的代码 */
  const codeHtml = ref('');

  /** 高亮代码 */
  watch(
    [() => props.code, () => props.language],
    () => {
      const code = props.code;
      if (!code) {
        codeLines.value = [1];
        codeHtml.value = '';
        return;
      }
      codeLines.value = code.split('\n').map((_, i) => i + 1);
      codeHtml.value = hljs.highlight(code, {
        language: props.language || 'vue'
      }).value;
    },
    { immediate: true }
  );
</script>

<style lang="scss">
  @use 'ele-admin-plus/es/style/util.scss' as *;

  .ele-code-viewer {
    display: flex;
    color: #e6edf3;
    background: #1e1e1e;
    border-radius: elVar('border-radius', 'base');
    box-sizing: border-box;
    overflow: auto;
    #{eleVarName('scrollbar', 'color')}: #5e5e5e;
    #{eleVarName('scrollbar', 'hover-color')}: #707070;

    & > pre {
      flex: 1;
      margin: 0;
      padding: 8px;
      box-sizing: border-box;
      font-family: monospace;
    }

    & > pre,
    & > .ele-code-viewer-line-numbers {
      height: max-content;
      min-height: 100%;
    }
  }

  .ele-code-viewer-line-numbers {
    flex-shrink: 0;
    color: #8b949e;
    font-family: monospace;
    padding: 8px 0;
    min-width: 38px;
    background: inherit;
    border-right: 1px solid #000;
    box-sizing: border-box;
    text-align: center;
    user-select: none;
    position: sticky;
    left: 0;

    & > div {
      max-height: 100%;
    }
  }
</style>
