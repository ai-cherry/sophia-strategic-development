import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh in development
      fastRefresh: process.env.NODE_ENV !== 'production',
    })
  ],

  // Build configuration optimized for production
  build: {
    // Output directory for production builds
    outDir: 'dist',

    // Generate source maps for debugging in production
    sourcemap: true,

    // Optimize bundle size
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true,
      },
    },

    // Chunk splitting strategy for optimal caching
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk for third-party libraries
          vendor: ['react', 'react-dom'],

          // UI components chunk
          ui: ['@mui/material', '@emotion/react', '@emotion/styled'],

          // Utilities chunk
          utils: ['lodash', 'date-fns', 'axios'],
        },

        // Optimize chunk naming for caching
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },

    // Target modern browsers for smaller bundles
    target: 'es2020',

    // Optimize asset handling
    assetsInlineLimit: 4096, // Inline assets smaller than 4kb

    // Enable CSS code splitting
    cssCodeSplit: true,
  },

  // Development server configuration
  server: {
    port: 3000,
    host: '0.0.0.0', // Allow external connections
    cors: true,

    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: process.env.VITE_SOPHIA_API_URL || 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  // Preview server configuration (for production builds)
  preview: {
    port: 3000,
    host: '0.0.0.0',
    cors: true,
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@services': resolve(__dirname, 'src/services'),
      '@store': resolve(__dirname, 'src/store'),
      '@types': resolve(__dirname, 'src/types'),
    },
  },

  // Environment variable handling
  envPrefix: 'VITE_',

  // CSS configuration
  css: {
    // Enable CSS modules
    modules: {
      localsConvention: 'camelCase',
    },

    // PostCSS configuration
    postcss: {
      plugins: [
        // Add autoprefixer for browser compatibility
        require('autoprefixer'),

        // Add cssnano for CSS minification in production
        ...(process.env.NODE_ENV === 'production'
          ? [require('cssnano')({ preset: 'default' })]
          : []
        ),
      ],
    },

    // CSS preprocessing
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
  },

  // Optimization configuration
  optimizeDeps: {
    // Pre-bundle dependencies for faster dev server startup
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'lodash',
    ],

    // Exclude dependencies that should not be pre-bundled
    exclude: ['@vite/client', '@vite/env'],
  },

  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __COMMIT_HASH__: JSON.stringify(process.env.lambda_labsGIT_COMMIT_SHA || 'dev'),
  },

  // Worker configuration
  worker: {
    format: 'es',
  },

  // Experimental features
  experimental: {
    // Enable build optimizations
    renderBuiltUrl: (filename, { hostType }) => {
      if (hostType === 'js') {
        return { js: `/${filename}` }
      } else {
        return { relative: true }
      }
    },
  },

  // Performance configuration
  esbuild: {
    // Drop console and debugger in production
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],

    // Enable JSX automatic runtime
    jsxInject: `import React from 'react'`,
  },

  // Plugin-specific configuration
  json: {
    namedExports: true,
    stringify: false,
  },

  // Legacy browser support (if needed)
  legacy: {
    buildSsrCjsExternalHeuristics: true,
  },
})
