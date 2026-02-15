import type { ProxyOptions } from 'vite';
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import { resolve } from 'node:path';
//import Compression from 'vite-plugin-compression';
import Components from 'unplugin-vue-components/vite';
import type { ComponentResolver } from 'unplugin-vue-components/types';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import { EleAdminResolver } from './components/utils/resolvers';
import { ComponentsResolver } from './src/components/resolvers';

export default defineConfig(({ /* command, */ mode }) => {
  //const isBuild = command === 'build';
  const isBuild = true;
  const env = loadEnv(mode, process.cwd());
  // 别名配置
  const alias = {
    '@/': resolve('src') + '/',
    '@shared/': resolve('../components') + '/',
    'vue-i18n': 'vue-i18n/dist/vue-i18n.cjs.js',
    'ele-admin-plus/es': resolve('components'),
    'ele-admin-plus': resolve('components')
  };
  // 插件配置
  const plugins = [vue(), vueJsx()];
  const componentsResolvers: (ComponentResolver | ComponentResolver[])[] = [
    ComponentsResolver()
  ];
  if (isBuild) {
    // 组件按需引入插件
    componentsResolvers.push(
      ElementPlusResolver({
        importStyle: 'sass'
      })
    );
    componentsResolvers.push(
      EleAdminResolver({
        importStyle: 'sass'
      })
    );
    // gzip压缩插件
    /* plugins.push(
      Compression({
        disable: !isBuild,
        threshold: 10240,
        algorithm: 'gzip',
        ext: '.gz'
      })
    ); */
  } else {
    // 开发环境全局安装
    alias['./as-needed'] = './global-import';
  }
  plugins.push(
    Components({
      dts: false,
      globsExclude: ['src/components/*/components/**'],
      resolvers: componentsResolvers
    })
  );
  // 接口地址代理配置
  const baseApi = env.VITE_API_URL;
  const proxyApi = env.VITE_API_PROXY_URL;
  const proxy: Record<string, string | ProxyOptions> = {};
  if (proxyApi) {
    const isRemoveBasePath = !proxyApi.endsWith(baseApi); // 接口代理时是否移除地址前缀
    proxy[baseApi] = {
      target: isRemoveBasePath
        ? proxyApi
        : proxyApi.substring(0, proxyApi.length - baseApi.length),
      rewrite: isRemoveBasePath
        ? (path) => path.replace(new RegExp(`^${baseApi}`), '')
        : void 0,
      changeOrigin: true
    };
  }
  return {
    resolve: { alias },
    plugins,
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/styles/variables.scss" as *;`
        }
      }
    },
    optimizeDeps: {
      include: [
        'echarts/core',
        'echarts/charts',
        'echarts/renderers',
        'echarts/components',
        'vue-echarts',
        'echarts-wordcloud',
        'sortablejs',
        'vuedraggable',
        'element-plus',
        'element-plus/es',
        ...[
          'ElAffix',
          'ElAlert',
          'ElAside',
          'ElAutocomplete',
          'ElAvatar',
          'ElBacktop',
          'ElBadge',
          'ElBreadcrumb',
          'ElBreadcrumbItem',
          'ElButton',
          'ElButtonGroup',
          'ElCalendar',
          'ElCard',
          'ElCarousel',
          'ElCarouselItem',
          'ElCascader',
          'ElCascaderPanel',
          'ElCheckbox',
          'ElCheckboxButton',
          'ElCheckboxGroup',
          'ElCol',
          'ElCollapse',
          'ElCollapseItem',
          'ElCollapseTransition',
          'ElColorPicker',
          'ElContainer',
          'ElConfigProvider',
          'ElDatePicker',
          'ElDialog',
          'ElDivider',
          'ElDrawer',
          'ElDropdown',
          'ElDropdownItem',
          'ElDropdownMenu',
          'ElEmpty',
          'ElFooter',
          'ElForm',
          'ElFormItem',
          'ElHeader',
          'ElIcon',
          'ElImage',
          'ElImageViewer',
          'ElInput',
          'ElInputNumber',
          'ElLink',
          'ElMain',
          'ElMenu',
          'ElMenuItem',
          'ElMenuItemGroup',
          'ElOption',
          'ElOptionGroup',
          'ElPageHeader',
          'ElPagination',
          'ElPopconfirm',
          'ElPopper',
          'ElPopover',
          'ElProgress',
          'ElRadio',
          'ElRadioButton',
          'ElRadioGroup',
          'ElRate',
          'ElRow',
          'ElScrollbar',
          'ElSelect',
          'ElSlider',
          'ElStep',
          'ElSteps',
          'ElSubMenu',
          'ElSwitch',
          'ElTabPane',
          'ElTable',
          'ElTableColumn',
          'ElTabs',
          'ElTag',
          'ElText',
          'ElTimePicker',
          'ElTimeSelect',
          'ElTimeline',
          'ElTimelineItem',
          'ElTooltip',
          'ElTransfer',
          'ElTree',
          'ElTreeV2',
          'ElTreeSelect',
          'ElUpload',
          'ElSpace',
          'ElSkeleton',
          'ElSkeletonItem',
          'ElStatistic',
          'ElCheckTag',
          'ElDescriptions',
          'ElDescriptionsItem',
          'ElResult',
          'ElSelectV2',
          'ElWatermark'
        ].map(
          (k) =>
            `element-plus/es/components/${k
              .replace(/([A-Z])/g, ' $1')
              .trim()
              .split(' ')
              .join('-')
              .toLowerCase()
              .substring('el-'.length)}/style/index`
        ),
        'element-plus/es/components/base/style/index',
        'element-plus/es/components/message/style/index',
        'element-plus/es/components/message-box/style/index',
        'element-plus/es/components/notification/style/index',
        'element-plus/es/components/loading/style/index',
        'element-plus/es/components/table-v2/style/index'
      ]
    },
    build: {
      target: 'chrome63',
      chunkSizeWarningLimit: 4000,
      assetsInlineLimit: 0
    },
    server: { proxy }
  };
});
