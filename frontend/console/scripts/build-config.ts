/** 打包配置 */
import type { UserConfigExport, PluginOption, LibraryFormats } from 'vite';
import { VuePathPlugin, DTSPlugin } from './build-plugin';
/** 打包时外部依赖 */
const EXTERNAL_BASE = [
  'vue',
  /^\.\//,
  /^\.\.\//,
  'element-plus',
  /^element-plus\//,
  /^@element-plus\//,
  'vue-router',
  'vuedraggable',
  'sortablejs',
  'cropperjs',
  /^cropperjs\//,
  /^@ant-design\//,
  '@amap/amap-jsapi-loader',
  'jsbarcode',
  'countup.js',
  'xgplayer',
  /^xgplayer\//,
  'unplugin-vue-components',
  'lodash-es',
  'exceljs'
];
/** 打包类型 */
const FORMAT = process.env.FORMAT as LibraryFormats;
/** 组件名称 */
const NAME = process.env.NAME as string;
/** 输入文件的完整路径 */
const INPUT = process.env.INPUT as string;
/** 输出文件的完整名称 */
const OUTPUT = process.env.OUTPUT as string;
/** 输出目录的完整路径 */
const TARGET = process.env.TARGET as string;
/** 输入目录的路径 */
const DIRECTORY = process.env.DIRECTORY as string;
/** 输出文件的名称 */
const FILE_NAME = OUTPUT?.replace?.('.js', '');
/** 是否输出 dts 文件 */
const OUT_DTS =
  (INPUT?.endsWith?.('.ts') ||
    INPUT?.endsWith?.('.vue') ||
    INPUT?.endsWith?.('.tsx')) &&
  FORMAT === 'es';
/** 是否压缩文件 */
const IS_MINIFY = INPUT?.endsWith?.('receiver-view.tsx');

/**
 * 打包时的配置
 */
export const buildOption: UserConfigExport = {
  build: {
    lib: {
      /** 组件名称 */
      name: NAME,
      /** 打包类型 */
      formats: [FORMAT],
      /** 输入文件完整路径 */
      entry: INPUT,
      /** 输出文件名称 */
      fileName: () => OUTPUT
    },
    rollupOptions: {
      /** 外部的库依赖 */
      external: EXTERNAL_BASE,
      /** 导出模式 */
      output: { exports: NAME === 'EleAdminPlus' ? 'named' : 'auto' }
    },
    /** 输出目录完整路径 */
    outDir: TARGET,
    /** 是否清空输出目录 */
    emptyOutDir: false,
    /** 是否报告 gzip 大小 */
    reportCompressedSize: false,
    /** 是否压缩文件 */
    minify: IS_MINIFY ? 'esbuild' : false
  },
  esbuild: IS_MINIFY ? { charset: 'ascii' } : void 0
};

/**
 * 打包时的插件
 */
export const buildPlugins: PluginOption[] = [
  VuePathPlugin(),
  ...(OUT_DTS ? [DTSPlugin(DIRECTORY, FILE_NAME)] : [])
];
