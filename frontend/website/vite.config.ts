import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import svgLoader from 'vite-svg-loader';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

/** 配置文件所在目录作为项目根，避免从 monorepo 其它目录启动时 public/、别名解析错误 */
const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: __dirname,
  plugins: [vue(), svgLoader()],
  resolve: {
    alias: {
      '@/': resolve(__dirname, 'src') + '/',
      '@shared/': resolve(__dirname, '../components') + '/'
    }
  },
  server: {
    port: 5175,
    proxy: {
      '/api/open': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    target: 'chrome63'
  }
});
