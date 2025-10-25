import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'
import { resolve } from 'path'
import { defineConfig, loadEnv } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
    const isProduction = mode === 'production' || command === 'build'

    // Загружаем переменные окружения
    const env = loadEnv(mode, process.cwd(), '')

    // Извлекаем домен из Cloudflare URL для allowedHosts
    const cloudflareUrl = env.VITE_CLOUDFLARE_TUNNEL_URL || env.CLOUDFLARE_TUNNEL_URL || ''
    const cloudflareDomain = cloudflareUrl.replace('https://', '').replace('http://', '')

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
                    cloudflareDomain,
                    '.trycloudflare.com'
                ].filter(Boolean),
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
                minify: 'esbuild',
                rollupOptions: {
                    input: {
                        main: resolve(__dirname, 'index.html'),
                    },
                    output: {
                        manualChunks: {
                            // Vendor chunks
                            'react-vendor': ['react', 'react-dom'],
                            'framer-motion': ['framer-motion'],
                            'router': ['react-router-dom'],
                            'ui': ['lucide-react'],
                            // Page chunks
                            'pages': [
                                './src/pages/HomePage.tsx',
                                './src/pages/NewsPage.tsx',
                                './src/pages/DigestPage.tsx',
                                './src/pages/EventsPage.tsx',
                                './src/pages/SettingsPage.tsx'
                            ],
                            // Component chunks
                            'components': [
                                './src/components/NewsCard.tsx',
                                './src/components/EventCard.tsx',
                                './src/components/DigestCard.tsx',
                                './src/components/OptimizedImage.tsx',
                                './src/components/LazyContent.tsx'
                            ],
                            // Admin chunk
                            'admin': [
                                './src/admin/AdminRoutes.tsx'
                            ]
                        },
                        chunkFileNames: (chunkInfo) => {
                            const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
                            return `js/[name]-[hash].js`;
                        },
                        entryFileNames: 'js/[name]-[hash].js',
                        assetFileNames: (assetInfo) => {
                            const info = assetInfo.name.split('.');
                            const ext = info[info.length - 1];
                            if (/\.(css)$/.test(assetInfo.name)) {
                                return `css/[name]-[hash].${ext}`;
                            }
                            return `assets/[name]-[hash].${ext}`;
                        },
                    },
                },
                chunkSizeWarningLimit: 1000,
            },
        }),
    }
})
