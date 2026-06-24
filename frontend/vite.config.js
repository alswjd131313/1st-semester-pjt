import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/gmsapi': {
        target: 'https://gms.ssafy.io',
        changeOrigin: true,
        secure: true,
      }
    }
  },
});