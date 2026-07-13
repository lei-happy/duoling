<!-- 天气预报插件（weatherwidget.org 第三方组件，异步加载脚本渲染，按内容自然高度完整显示） -->
<template>
  <div class="weather-widget">
    <div
      :id="WIDGET_ID"
      v="1.3"
      loc="auto"
      :a="WIDGET_CONFIG"
    >
      <a
        :href="WIDGET_LINK"
        :id="`${WIDGET_ID}_u`"
        target="_blank"
        rel="noopener"
      >
        天气插件
      </a>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { onMounted } from 'vue';

  defineOptions({ name: 'WeatherWidget' });

  /** weatherwidget.org 分配的组件唯一 id */
  const WIDGET_ID = 'ww_87063107654a2';
  /** 组件外观配置（横向布局、中文、白底） */
  const WIDGET_CONFIG = JSON.stringify({
    t: 'horizontal',
    lang: 'zh',
    sl_lpl: 1,
    ids: [],
    font: 'Arial',
    sl_ics: 'one_a',
    sl_sot: 'celsius',
    cl_bkg: '#FFFFFF',
    cl_font: '#000000',
    cl_cloud: '#d4d4d4',
    cl_persp: '#2196F3',
    cl_sun: '#FFC107',
    cl_moon: '#FFC107',
    cl_thund: '#FF5722'
  });
  const WIDGET_LINK = 'https://weatherwidget.org/zh/';
  /** 官方渲染脚本地址（与组件 id 绑定） */
  const WIDGET_SCRIPT_SRC = `https://app3.weatherwidget.org/js/?id=${WIDGET_ID}`;
  const WIDGET_SCRIPT_ID = 'weatherwidget-org-js';

  /**
   * 注入官方脚本，脚本执行时会查找对应 id 的容器并渲染。
   * 为兼容 SPA 重新挂载场景，挂载时移除旧脚本再重新插入以触发重新渲染。
   */
  const loadWidgetScript = () => {
    document.getElementById(WIDGET_SCRIPT_ID)?.remove();
    const script = document.createElement('script');
    script.id = WIDGET_SCRIPT_ID;
    script.async = true;
    script.src = WIDGET_SCRIPT_SRC;
    document.body.appendChild(script);
  };

  onMounted(loadWidgetScript);
</script>

<style lang="scss" scoped>
  .weather-widget {
    width: 100%;
    display: flex;
    justify-content: center;
    text-align: center;

    /* 让组件块水平居中，不强制拉伸，避免内容靠左产生右侧留白 */
    :deep(> div) {
      margin: 0 auto;
    }

    :deep(iframe) {
      border: none;
    }

    :deep(a) {
      color: var(--el-text-color-secondary);
      font-size: 12px;
      text-decoration: none;
    }
  }
</style>
