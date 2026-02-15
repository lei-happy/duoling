<template>
  <ele-card header="代码编辑器" :body-style="{ padding: '12px' }">
    <div style="display: flex; align-items: center; margin-bottom: 12px">
      <div>主题：</div>
      <div style="flex: 1">
        <el-select
          v-model="theme"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
        >
          <el-option value="vs" label="Visual Studio" />
          <el-option value="vs-dark" label="Visual Studio Dark" />
          <el-option value="hc-light" label="High Contrast" />
          <el-option value="hc-black" label="High Contrast Dark" />
        </el-select>
      </div>
      <div>&emsp;语言：</div>
      <div style="flex: 1">
        <el-select
          v-model="language"
          class="ele-fluid"
          :popper-options="{ strategy: 'fixed' }"
          @change="handleLanguageChange"
        >
          <el-option
            v-for="item in languageNames"
            :key="item"
            :value="item"
            :label="item"
          />
        </el-select>
      </div>
    </div>
    <div style="border: 1px solid var(--el-border-color)">
      <monaco-editor
        v-model="code"
        :language="language"
        :theme="theme"
        style="height: 460px"
      />
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import MonacoEditor from '@/components/MonacoEditor/index.vue';
  import { codes } from './demo-codes';

  const languageNames = Object.keys(codes);

  /** 代码内容 */
  const code = ref('');

  /** 语言 */
  const language = ref('typescript');

  /** 主题 */
  const theme = ref('vs-dark');

  /** 切换代码内容 */
  const handleLanguageChange = () => {
    code.value = codes[language.value];
  };

  handleLanguageChange();
</script>
