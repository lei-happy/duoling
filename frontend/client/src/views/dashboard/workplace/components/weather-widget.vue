<!-- 天气预报插件（天气网第三方 iframe 组件） -->
<template>
  <div class="weather-widget">
    <iframe
      class="weather-widget-iframe"
      width="421"
      height="60"
      src="https://i.tianqi.com/?c=code&a=getcode&id=14&icon=1"
      frameborder="0"
      title="天气预报"
    ></iframe>
  </div>
</template>

<script lang="ts" setup>
  defineOptions({ name: 'WeatherWidget' });
</script>

<style lang="scss" scoped>
  .weather-widget {
    width: 100%;
    display: flex;
    margin-left: 0;
    justify-content: flex-start;
    overflow: visible;
  }

  .weather-widget-iframe {
    border: none;
    max-width: 100%;
    height: 60px;
    flex-shrink: 0;
  }
</style>
