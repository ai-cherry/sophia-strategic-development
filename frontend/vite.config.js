import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Build configuration optimized for Vercel
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['lucide-react', '@radix-ui/react-slot'],
          router: ['react-router-dom'],
          charts: ['recharts'],
          utils: ['clsx', 'tailwind-merge', 'class-variance-authority']
        }
      }
    },
    // Optimize for production
    minify: 'esbuild',
    target: 'es2020',
    chunkSizeWarningLimit: 1000,
  },
  // Server configuration for development - ALLOW ALL HOSTS
  server: {
    port: 3000,
    host: '0.0.0.0',
    cors: true,
    allowedHosts: 'all',
    hmr: {
      host: 'localhost'
    }
  },
  // Preview configuration
  preview: {
    port: 3000,
    host: '0.0.0.0',
    cors: true
  },
  // Environment variable configuration
  envPrefix: ['VITE_'],
  // Define global constants
  define: {
    // Make build info available to the app
    __BUILD_DATE__: JSON.stringify(new Date().toISOString()),
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'lucide-react',
      'recharts',
      'axios',
      'framer-motion'
    ],
  },
})

