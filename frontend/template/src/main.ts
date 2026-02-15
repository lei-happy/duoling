import { createApp } from 'vue';
import App from './App.vue';
import store from './store';
import router from './router';
import permission from './utils/permission';
import i18n from './i18n';
import installer from './as-needed';
import { iconsInstaller } from '@/components/IconSelect/util';
import 'element-plus/theme-chalk/display.css';
import 'ele-admin-plus/es/style/nprogress.scss';
import './styles/themes';
import './styles/index.scss';

// 设置高德地图密钥
const mapKeySecret = import.meta.env.VITE_MAP_SECRET;
if (mapKeySecret) {
  // @ts-ignore
  window._AMapSecurityConfig = { securityJsCode: mapKeySecret };
}

const app = createApp(App);

app.use(store);
app.use(router);
app.use(permission);
app.use(i18n);
app.use(installer);
app.use(iconsInstaller);

app.mount('#app');
