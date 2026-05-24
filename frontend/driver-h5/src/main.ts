import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { Lazyload, allowMultipleToast } from 'vant';
import 'vant/lib/index.css';
import 'vant/es/toast/style';
import 'vant/es/dialog/style';
import 'vant/es/notify/style';
import 'vant/es/image-preview/style';

import App from './App.vue';
import router from './router';
import './styles/index.scss';

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(Lazyload);

allowMultipleToast(false);

app.mount('#app');
