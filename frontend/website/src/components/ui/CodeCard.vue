<template>
  <div class="codecard">
    <div class="codecard-bar">
      <b>{{ filename }}</b>
      <button type="button" class="codecard-copy" @click="copy">
        {{ copied ? '已复制' : '复制' }}
      </button>
    </div>
    <!-- 高亮用 span 包裹，内容是本仓库内写死的常量，不接受外部输入 -->
    <pre :aria-label="filename" v-html="html" />
    <div v-if="$slots.foot" class="codecard-foot">
      <slot name="foot" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  filename: string;
  /** 带语法高亮 span 的代码片段 */
  html: string;
  /** 点复制时写入剪贴板的原文 */
  raw: string;
}>();

const copied = ref(false);
let timer: ReturnType<typeof setTimeout> | undefined;

async function copy() {
  try {
    await navigator.clipboard.writeText(props.raw);
    copied.value = true;
    clearTimeout(timer);
    timer = setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch {
    // 浏览器拒绝剪贴板权限时，用户还能手动选中复制，不额外弹提示打断
  }
}
</script>
