<template>
  <div id="app">
    <a class="skip-link" href="#main">跳到正文</a>
    <SiteHeader />
    <main id="main">
      <RouterView />
    </main>
    <SiteFooter />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import SiteHeader from '@/layouts/SiteHeader.vue';
import SiteFooter from '@/layouts/SiteFooter.vue';
</script>

<style lang="scss">
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style>
