/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 客户端应用地址，如 http://localhost:5174 */
  readonly VITE_CLIENT_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
