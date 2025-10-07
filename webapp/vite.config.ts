import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/webapp',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 3000,
    host: true, // Allow external connections
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'festival-seriously-facilitate-william.trycloudflare.com',
      '.trycloudflare.com' // Allow all trycloudflare.com subdomains
    ],
    headers: {
      'Cross-Origin-Embedder-Policy': 'unsafe-none',
      'Cross-Origin-Opener-Policy': 'unsafe-none',
      'Cross-Origin-Resource-Policy': 'cross-origin',
    },
    // Proxy убран - теперь Flask обрабатывает все запросы
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
