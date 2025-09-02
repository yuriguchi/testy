/// <reference types="vite/client" />
/// <reference types="vite-plugin-svgr/client" />

interface ImportMetaEnv {
  readonly VITE_APP_API_ROOT: string
  readonly VITE_APP_REPO_URL: string
  readonly VITE_APP_BUG_REPORT_URL: string
  readonly VITE_MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
