<template>
  <header class="sec-head" :class="{ reveal: reveal }">
    <span v-if="eyebrow" class="eyebrow">{{ eyebrow }}</span>
    <h2 class="h-sec">
      <slot name="title">{{ title }}</slot>
    </h2>
    <p v-if="$slots.default" class="lede"><slot /></p>
  </header>
</template>

<script setup lang="ts">
/** 区块标题：眉题 + 主标题 + 导语，五个页面共用同一套间距节奏。 */
withDefaults(
  defineProps<{
    eyebrow?: string;
    /** 纯文本标题；需要高亮某几个字时改用 title 插槽 */
    title?: string;
    reveal?: boolean;
  }>(),
  { eyebrow: '', title: '', reveal: true }
);
</script>
