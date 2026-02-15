<template>
  <div id="app">
    <NavHeader v-if="!isFullPage" />
    <main>
      <router-view />
    </main>
    <SiteFooter v-if="!isFullPage" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavHeader from '@/components/NavHeader.vue'
import SiteFooter from '@/components/SiteFooter.vue'

const route = useRoute()
const isFullPage = computed(() => route.meta.fullPage === true)
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
