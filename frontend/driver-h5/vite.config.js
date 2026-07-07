import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import Components from 'unplugin-vue-components/vite';
import { VantResolver } from '@vant/auto-import-resolver';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
var __dirname = dirname(fileURLToPath(import.meta.url));
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd());
    var baseApi = env.VITE_API_URL || '/api/driver';
    var proxyApi = env.VITE_API_PROXY_URL || 'http://localhost:8000';
    var proxy = {};
    if (proxyApi) {
        proxy[baseApi] = {
            target: proxyApi,
            changeOrigin: true
        };
        try {
            var openTarget = new URL(proxyApi.startsWith('http') ? proxyApi : "http://".concat(proxyApi));
            proxy['/api/open'] = {
                target: "".concat(openTarget.protocol, "//").concat(openTarget.host),
                changeOrigin: true
            };
            proxy['/uploads'] = {
                target: "".concat(openTarget.protocol, "//").concat(openTarget.host),
                changeOrigin: true
            };
        }
        catch (_b) {
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
                    additionalData: "@use \"@/styles/variables.scss\" as *;"
                }
            }
        },
        server: {
            port: 5176,
            host: true,
            proxy: proxy
        },
        build: {
            target: 'chrome63',
            chunkSizeWarningLimit: 2000
        }
    };
});
