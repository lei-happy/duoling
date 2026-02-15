<!-- 路由出口 -->
<template>
  <router-view v-slot="{ route, Component }">
    <template v-if="!transitionName || transitionName === 'none'">
      <keep-alive v-if="pageKeepAlive" :include="keepAliveInclude" :max="10">
        <component :key="route.path" :is="Component" />
      </keep-alive>
      <component v-else :key="route.path" :is="Component" />
    </template>
    <transition v-else :name="transitionName" mode="out-in" appear>
      <keep-alive v-if="pageKeepAlive" :include="keepAliveInclude" :max="10">
        <component :key="route.path" :is="Component" />
      </keep-alive>
      <component v-else :key="route.path" :is="Component" />
    </transition>
  </router-view>
</template>

<script lang="ts" setup>
  import { storeToRefs } from 'pinia';
  import { useTabStore } from '@/store/modules/tab';
  import { useThemeStore } from '@/store/modules/theme';

  defineOptions({ name: 'RouterLayout' });

  const tabStore = useTabStore();
  const { keepAliveInclude, pageKeepAlive } = storeToRefs(tabStore);

  const themeStore = useThemeStore();
  const { transitionName } = storeToRefs(themeStore);
</script>
