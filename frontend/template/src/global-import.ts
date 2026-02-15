/** 全局安装(开发环境) */
import type { App, Plugin } from 'vue';
import ElementPlus from 'element-plus';
import EleAdminPlus from 'ele-admin-plus';
import 'element-plus/theme-chalk/src/index.scss';
import 'ele-admin-plus/es/style/index.scss';
import 'cropperjs/dist/cropper.css';
import 'xgplayer/dist/index.min.css';
import * as components from '@/components/lite';

const installer: Plugin = {
  install(app: App) {
    app.use(ElementPlus);
    app.use(EleAdminPlus);
  }
};

export default installer;

/** 让 vite 能扫描到公共组件用到的依赖, 避免首次运行时频繁更新依赖刷新页面 */
export { components };
