import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const isProduction = mode === 'production' || command === 'build'
  
  return {
    plugins: [react()],
    base: '/webapp',
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    // Конфигурация только для development
    ...(command === 'serve' && {
      server: {
        port: 3000,
        host: true,
        allowedHosts: [
          'localhost',
          '127.0.0.1',
          'expressed-nurse-drive-original.trycloudflare.com',
          '.trycloudflare.com'
        ],
        headers: {
          'Cross-Origin-Embedder-Policy': 'unsafe-none',
          'Cross-Origin-Opener-Policy': 'unsafe-none',
          'Cross-Origin-Resource-Policy': 'cross-origin',
        },
        // Proxy для API в dev режиме
        proxy: {
          '/api': {
            target: 'http://localhost:8001',
            changeOrigin: true,
            secure: false,
          },
          '/webapp': {
            target: 'http://localhost:8001',
            changeOrigin: true,
            secure: false,
          },
        },
      },
    }),
    // Конфигурация для production
    ...(isProduction && {
      build: {
        outDir: 'dist',
        assetsDir: 'assets',
        sourcemap: false,
        rollupOptions: {
          input: {
            main: resolve(__dirname, 'index.html'),
          },
        },
      },
    }),
  }
})
