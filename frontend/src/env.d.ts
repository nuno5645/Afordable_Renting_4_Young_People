interface ImportMetaEnv {
  readonly VITE_APP_ENV: 'local' | 'prod'
  readonly VITE_NGROK_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 