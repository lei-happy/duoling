/// <reference types="vite/client" />

/** 与 vite-svg-loader 一致：无查询参数时可能被 Vite 加上 ?import，导致未走 loader；品牌 SVG 请用 ?component */
declare module '*.svg?component' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<object, object, unknown>;
  export default component;
}

interface ImportMetaEnv {
  /** 客户端应用地址，如 http://localhost:5174 */
  readonly VITE_CLIENT_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
