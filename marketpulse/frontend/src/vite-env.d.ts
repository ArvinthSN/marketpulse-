/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module 'react-plotly.js' {
  import type { ComponentType } from 'react';
  const Plot: ComponentType<any>;
  export default Plot;
}
