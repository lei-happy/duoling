<!-- 路由出口 -->
<template>
  <router-view v-slot="{ route, Component }">
    <!-- 无过渡：直接渲染，可选 keep-alive -->
    <template v-if="!transitionName || transitionName === 'none'">
      <keep-alive v-if="pageKeepAlive" :include="keepAliveInclude" :max="10">
        <component :key="route.path" :is="Component" />
      </keep-alive>
      <component v-else :key="route.path" :is="Component" />
    </template>
    <!--
      开启页面缓存时不套 transition：KeepAlive 是稳定的外壳，路由只换内部 component，
      out-in 等不到「离场结束 → 新页入场」，中间会一直白屏（货源/运力大厅等同构页切换必现）。
    -->
    <keep-alive
      v-else-if="pageKeepAlive"
      :include="keepAliveInclude"
      :max="10"
    >
      <component :key="route.path" :is="Component" />
    </keep-alive>
    <!-- 未开缓存：component 作为 transition 唯一直接子节点，out-in 才可靠 -->
    <transition v-else :name="transitionName" mode="out-in" appear>
      <component :key="route.path" :is="Component" />
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
