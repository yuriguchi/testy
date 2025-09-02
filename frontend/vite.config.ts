import react from "@vitejs/plugin-react"
import { defineConfig, splitVendorChunkPlugin } from "vite"
import svgr from "vite-plugin-svgr"
import tsconfigPaths from "vite-tsconfig-paths"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr(),
    tsconfigPaths(),
    splitVendorChunkPlugin(),
  ],
  server: {
    port: 3000,
    host: "127.0.0.1",
  },
  preview: {
    port: 4000,
  },
  build: {
    outDir: "build",
    assetsDir: "static",
    rollupOptions: {
      input: {
        app: "./index.html",
      },
      output: {
        manualChunks: (module: string) => {
          if (module.includes("node_modules")) {
            return "npm-packages"
          }
          return null
        },
      },
    },
  },
  resolve: {
    alias: [{ find: /^~/, replacement: "" }],
  },
})
