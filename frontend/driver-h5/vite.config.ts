import type { ProxyOptions } from 'vite';
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import Components from 'unplugin-vue-components/vite';
import { VantResolver } from '@vant/auto-import-resolver';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());

  const baseApi = env.VITE_API_URL || '/api/driver';
  const proxyApi = env.VITE_API_PROXY_URL || 'http://localhost:8000';
  const proxy: Record<string, string | ProxyOptions> = {};

  if (proxyApi) {
    proxy[baseApi] = {
      target: proxyApi,
      changeOrigin: true
    };
    try {
      const openTarget = new URL(
        proxyApi.startsWith('http') ? proxyApi : `http://${proxyApi}`
      );
      proxy['/api/open'] = {
        target: `${openTarget.protocol}//${openTarget.host}`,
        changeOrigin: true
      };
      proxy['/uploads'] = {
        target: `${openTarget.protocol}//${openTarget.host}`,
        changeOrigin: true
      };
    } catch {
      /* ignore */
    }
  }

  return {
    root: __dirname,
    plugins: [
      vue(),
      vueJsx(),
      Components({
        dts: 'src/components.d.ts',
        resolvers: [VantResolver()]
      })
    ],
    resolve: {
      alias: {
        '@/': resolve(__dirname, 'src') + '/',
        '@shared/': resolve(__dirname, '../components') + '/'
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@use "@/styles/variables.scss" as *;`
        }
      }
    },
    server: {
      port: 5176,
      host: true,
      proxy
    },
    build: {
      target: 'chrome63',
      chunkSizeWarningLimit: 2000
    }
  };
});
