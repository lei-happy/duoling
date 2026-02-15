<!-- eslint-disable vue/no-v-html -->
<template>
  <div
    v-html="content"
    :class="[
      { 'ele-tinymce-viewer': !darkMode },
      { 'ele-tinymce-viewer-dark': darkMode }
    ]"
  ></div>
</template>

<script lang="ts" setup>
  import { storeToRefs } from 'pinia';
  import { useThemeStore } from '@/store/modules/theme';

  defineOptions({ name: 'TinymceViewer' });

  defineProps<{
    /** 内容 */
    content?: string;
  }>();

  const themeStore = useThemeStore();
  const { darkMode } = storeToRefs(themeStore);
</script>

<style lang="scss">
  .ele-tinymce-viewer {
    font-family:
      -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
      Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.4;
    margin: 1rem;

    table {
      border-collapse: collapse;
    }
    /* Apply a default padding if legacy cellpadding attribute is missing */
    table:not([cellpadding]) th,
    table:not([cellpadding]) td {
      padding: 0.4rem;
    }
    /* Set default table styles if a table has a positive border attribute
   and no inline css */
    table[border]:not([border='0']):not([style*='border-width']) th,
    table[border]:not([border='0']):not([style*='border-width']) td {
      border-width: 1px;
    }
    /* Set default table styles if a table has a positive border attribute
   and no inline css */
    table[border]:not([border='0']):not([style*='border-style']) th,
    table[border]:not([border='0']):not([style*='border-style']) td {
      border-style: solid;
    }
    /* Set default table styles if a table has a positive border attribute
   and no inline css */
    table[border]:not([border='0']):not([style*='border-color']) th,
    table[border]:not([border='0']):not([style*='border-color']) td {
      border-color: #ccc;
    }
    figure {
      display: table;
      margin: 1rem auto;
    }
    figure figcaption {
      color: #999;
      display: block;
      margin-top: 0.25rem;
      text-align: center;
    }
    hr {
      border-color: #ccc;
      border-style: solid;
      border-width: 1px 0 0 0;
    }
    code {
      background-color: #e8e8e8;
      border-radius: 3px;
      padding: 0.1rem 0.2rem;
    }
    .mce-content-body:not([dir='rtl']) blockquote {
      border-left: 2px solid #ccc;
      margin-left: 1.5rem;
      padding-left: 1rem;
    }
    .mce-content-body[dir='rtl'] blockquote {
      border-right: 2px solid #ccc;
      margin-right: 1.5rem;
      padding-right: 1rem;
    }
  }

  /** 暗黑模式 */
  .ele-tinymce-viewer-dark {
    color: #dfe0e4;
    font-family:
      -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
      Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.4;
    margin: 1rem;

    a {
      color: #4099ff;
    }
    table {
      border-collapse: collapse;
    }
    /* Apply a default padding if legacy cellpadding attribute is missing */
    table:not([cellpadding]) th,
    table:not([cellpadding]) td {
      padding: 0.4rem;
    }
    /* Set default table styles if a table has a positive border attribute
   and no inline css */
    table[border]:not([border='0']):not([style*='border-width']) th,
    table[border]:not([border='0']):not([style*='border-width']) td {
      border-width: 1px;
    }
    /* Set default table styles if a table has a positive border attribute
   and no inline css */
    table[border]:not([border='0']):not([style*='border-style']) th,
    table[border]:not([border='0']):not([style*='border-style']) td {
      border-style: solid;
    }
    /* Set default table styles if a table has a positive border attribute
   and no inline css */
    table[border]:not([border='0']):not([style*='border-color']) th,
    table[border]:not([border='0']):not([style*='border-color']) td {
      border-color: #6d737b;
    }
    figure {
      display: table;
      margin: 1rem auto;
    }
    figure figcaption {
      color: #8a8f97;
      display: block;
      margin-top: 0.25rem;
      text-align: center;
    }
    hr {
      border-color: #6d737b;
      border-style: solid;
      border-width: 1px 0 0 0;
    }
    code {
      background-color: #6d737b;
      border-radius: 3px;
      padding: 0.1rem 0.2rem;
    }
    .mce-content-body:not([dir='rtl']) blockquote {
      border-left: 2px solid #6d737b;
      margin-left: 1.5rem;
      padding-left: 1rem;
    }
    .mce-content-body[dir='rtl'] blockquote {
      border-right: 2px solid #6d737b;
      margin-right: 1.5rem;
      padding-right: 1rem;
    }
  }
</style>
