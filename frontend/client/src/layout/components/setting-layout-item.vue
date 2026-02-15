<!-- 常用布局 -->
<template>
  <div class="ele-setting-layout-item" :class="{ 'is-active': active }">
    <div class="ele-setting-layout-item-cover" :style="coverStyle">
      <template v-if="cover">
        <template v-if="typeof cover === 'string'">
          <component v-if="LAYOUT_COVERS[cover]" :is="LAYOUT_COVERS[cover]" />
          <div
            v-else
            class="ele-setting-layout-item-cover-img"
            :style="{
              background: cover.startsWith('url(')
                ? cover
                : `url(${cover}) center / 100% 100%`
            }"
          ></div>
        </template>
        <component v-else :is="cover" />
      </template>
      <IconImage v-else />
    </div>
    <div class="ele-setting-layout-item-label">{{ title }}</div>
  </div>
</template>

<script lang="ts" setup>
  import type { PropType, Component, CSSProperties } from 'vue';
  import IconImage from './covers/icon-image.vue';
  import * as LAYOUT_COVERS from './covers';

  defineProps({
    title: String,
    cover: [String, Object, Function] as PropType<string | Component>,
    active: Boolean,
    coverStyle: Object as PropType<CSSProperties>
  });
</script>
