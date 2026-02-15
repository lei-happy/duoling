<template>
  <ele-page>
    <ele-card header="编辑器">
      <byte-md-editor v-model="content" height="520px" :config="config" />
    </ele-card>
    <ele-card header="解析器">
      <byte-md-viewer
        :value="content"
        :config="{ plugins: [gfm(), highlight()] }"
        style="max-width: 880px; margin: 0 auto; padding: 24px"
      />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import ByteMdEditor from '@/components/ByteMdEditor/index.vue';
  import ByteMdViewer from '@/components/ByteMdViewer/index.vue';
  /** 中文语言文件 */
  import zh_Hans from 'bytemd/locales/zh_Hans.json';
  /** 链接/删除线/复选框/表格等插件 */
  import gfm from '@bytemd/plugin-gfm';
  /** 插件的中文语言文件 */
  import zh_HansGfm from '@bytemd/plugin-gfm/locales/zh_Hans.json';
  /** 代码高亮插件 */
  import highlight from '@bytemd/plugin-highlight';
  /** 代码高亮插件样式 */
  import 'highlight.js/styles/github-dark.css';
  //import 'highlight.js/styles/github.css';
  /** 预览界面的样式, 这里用的github的markdown主题 */
  //import 'github-markdown-css/github-markdown-dark.css';
  import 'github-markdown-css/github-markdown-light.css';
  import { getDemoMD } from '@/api/example';

  defineOptions({ name: 'ExtensionMarkdown' });

  /** 编辑器内容 */
  const content = ref('');

  /** 配置 */
  const config = reactive({
    locale: zh_Hans,
    plugins: [gfm({ locale: zh_HansGfm }), highlight()],
    editorConfig: { lineNumbers: true },
    uploadImages: async (files: File[]) => {
      const result: Record<'url' | 'alt' | 'title', string>[] = [];
      files.forEach((file) => {
        result.push({
          url: 'https://cdn.eleadmin.com/20200610/4Z0QR2L0J1XStxBh99jVJ8qLfsGsOgjU.jpg',
          alt: file.name,
          title: ''
        });
      });
      return result;
    }
  });

  //
  getDemoMD()
    .then((res) => {
      content.value = res;
    })
    .catch((e) => {
      console.error(e);
    });
</script>

<style lang="scss">
  .markdown-body .highlight pre,
  .markdown-body pre {
    color: #e6edf3;
    background-color: #161b22;
  }
</style>
