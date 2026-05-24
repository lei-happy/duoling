<template>
  <van-tabbar v-model="active" route safe-area-inset-bottom fixed>
    <van-tabbar-item to="/home" icon="home-o" name="home">工作台</van-tabbar-item>
    <van-tabbar-item to="/task" icon="orders-o" name="task">任务</van-tabbar-item>
    <van-tabbar-item to="/finance" icon="balance-o" name="finance">收入</van-tabbar-item>
    <van-tabbar-item to="/profile" icon="user-o" name="profile">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const active = computed(() => (route.meta?.tab as string) || 'home');
</script>
