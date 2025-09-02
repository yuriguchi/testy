/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly NODE_ENV: string
  readonly VITE_APP_API_ROOT: string
  readonly VITE_APP_REPO_URL: string
  readonly VITE_APP_BUG_REPORT_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
