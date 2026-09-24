import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: null,
      devOptions: {
        enabled: true,
        type: 'module',
      },
      workbox: {
        inlineWorkboxRuntime: true,
        cleanupOutdatedCaches: true,
        navigateFallback: '/index.html',
        globPatterns: ['**/*.{js,css,html,png,svg,jpg}']
      },
      includeAssets: [
        'favicon.svg',
        'apple-touch-icon-180x180.png',
        'maskable-icon-512x512.png'
      ],
      manifest: {
        name: 'Mon application',
        short_name: 'Mon app',
        description: 'Description de mon application',
        theme_color: "#ffffff",
        background_color: "#ffffff",
        display: 'standalone',
        icons: [
          {
            "src": "pwa-64x64.png",
            "sizes": "64x64",
            "type": "image/png"
          },
          {
            "src": "pwa-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
          },
          {
            "src": "pwa-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
          },
          {
            "src": "maskable-icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable"
          }
        ]
      }
    }),
    vueDevTools({
      ...(process.env.EDITOR ? { launchEditor: process.env.EDITOR } : {}),
    }),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/friends': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/users': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/messages': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/badges': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/getbadge': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/recipe': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/upload': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/login': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/me': {
        target: 'http://backend:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://backend:5000',
        ws: true,
        changeOrigin: true
      }
    }
  }
})
