<template>
  <ele-card header="代码差异对比" :body-style="{ padding: '12px' }">
    <div style="border: 1px solid var(--el-border-color)">
      <monaco-editor
        v-model="code"
        :language="language"
        v-model:original="original"
        :original-language="originalLanguage"
        :diff="true"
        style="height: 460px"
      />
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import MonacoEditor from '@/components/MonacoEditor/index.vue';

  /** 代码内容 */
  const code = ref(`/**
 * 下载文件
 * @param data 二进制数据
 * @param name 文件名
 * @param type 文件类型
 */
export function download(data, name, type) {
  const blob = new Blob([data], { type: type || 'application/octet-stream' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * 深度克隆
 * @param value 对象
 */
export function cloneDeep(value) {
  const cache = new WeakMap();
  const clone = (value) => {
    if (typeof value !== 'object' || value == null) {
      return value;
    }
    // 处理 Date 对象
    if (value instanceof Date) {
      return new Date(value);
    }
    // 处理 RegExp 对象
    if (value instanceof RegExp) {
      return new RegExp(value.source, value.flags);
    }
    // 处理函数
    if (typeof value === 'function') {
      return value;
    }
    // 处理循环引用
    if (cache.has(value)) {
      return cache.get(value);
    }
    const result = Array.isArray(value) ? [] : {};
    cache.set(value, result);
    for (const key of Reflect.ownKeys(value)) {
      result[key] = clone(value[key]);
    }
    return result;
  };
  return clone(value);
}
`);

  /** 代码语言 */
  const language = ref('javascript');

  /** 原始代码内容 */
  const original = ref(`/**
 * 下载文件
 * @param data 二进制数据
 * @param name 文件名
 */
export function download(data, name) {
  const blob = new Blob([data], { type: 'application/octet-stream' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * 深度克隆
 * @param value 对象
 */
export function cloneDeep(value) {
  const cache = new WeakMap();
  const clone = (value) => {
    if (typeof value !== 'object' || value === null) {
      return value;
    }
    if (cache.has(value)) {
      return cache.get(value);
    }
    const result = Array.isArray(value) ? [] : {};
    cache.set(value, result);
    for (const key of Reflect.ownKeys(value)) {
      result[key] = clone(value[key]);
    }
    return result;
  };
  return clone(value);
}
`);

  /** 原始代码语言 */
  const originalLanguage = ref('javascript');
</script>
