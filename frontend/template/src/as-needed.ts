/** 按需引入(生产环境) */
import type { App, Plugin } from 'vue';

const installer: Plugin = {
  install(_app: App) {}
};

export default installer;
