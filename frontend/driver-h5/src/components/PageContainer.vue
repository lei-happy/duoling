<template>
  <div class="page-container" :class="{ 'has-tabbar': showTabbar }">
    <van-nav-bar
      v-if="showNav"
      :title="title"
      :left-arrow="!hideBack"
      :fixed="navFixed"
      :placeholder="navFixed"
      :border="false"
      @click-left="onBack"
    >
      <template v-if="$slots.right" #right>
        <slot name="right" />
      </template>
    </van-nav-bar>
    <div class="page-body" :class="{ 'with-nav': showNav && navFixed }">
      <slot />
    </div>
    <DriverTabbar v-if="showTabbar" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import DriverTabbar from './DriverTabbar.vue';

interface Props {
  title?: string;
  showNav?: boolean;
  hideBack?: boolean;
  navFixed?: boolean;
  showTabbar?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  showNav: true,
  hideBack: false,
  navFixed: true,
  showTabbar: false
});

const router = useRouter();

function onBack() {
  if (window.history.length > 1) router.back();
  else router.replace('/home');
}

// 显式引用避免 vue-tsc 误报
void props;
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: $bg-page;
  padding-bottom: $safe-area-bottom;
}
.page-container.has-tabbar {
  padding-bottom: calc(50px + #{$safe-area-bottom});
}
.page-body {
  min-height: 100vh;
}
</style>
