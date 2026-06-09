import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  publicDir: resolve(__dirname, '../logo'),
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://weibo-daily-sentence.zeabur.app',
        changeOrigin: true,
        secure: true
      }
    },
    fs: {
      allow: ['..']
    }
  }
})
