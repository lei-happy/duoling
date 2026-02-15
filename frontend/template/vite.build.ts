/**
 * 打包配置
 */
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import { buildOption, buildPlugins } from './scripts/build-config';

export default defineConfig({
  ...buildOption,
  mode: 'production',
  publicDir: false,
  plugins: [vue(), vueJsx(), ...buildPlugins],
  css: {
    preprocessorOptions: {
      scss: {
        api: 'legacy',
        outputStyle: 'expanded'
      } as any
    }
  }
});
