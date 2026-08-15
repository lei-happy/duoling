import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './styles/index.scss';
import './styles/components.scss';

// 官网不引组件库：这里的每个控件都按品牌设计系统手写，
// 引一整套 UI 库既会带来默认组件的观感，也会白白多几百 KB。
createApp(App).use(router).mount('#app');
