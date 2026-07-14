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
    />
  </div>
</template>

<script lang="ts" setup>
  defineOptions({ name: 'WeatherWidget' });
</script>

<style lang="scss" scoped>
  .weather-widget {
    width: 100%;
    display: flex;
    margin-left: 10px;
    justify-content: flex-start;
  }

  .weather-widget-iframe {
    border: none;
    max-width: 100%;
  }
</style>
