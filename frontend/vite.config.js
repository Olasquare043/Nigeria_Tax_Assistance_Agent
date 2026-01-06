
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    port: 3000,
    host: true, // Allows access from other devices on network
    open: true, // Automatically open browser
    proxy: {
      // Proxy API requests to your backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Remove /api prefix when forwarding to backend
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    },
    // Enable CORS for development
    cors: true,
    // Hot module replacement
    hmr: {
      overlay: true
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable sourcemaps for faster builds
    minify: 'terser', // Minify JavaScript
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        drop_debugger: true
      }
    },
    // Optimize chunk splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks
          'react-vendor': ['react', 'react-dom'],
          'icons': ['react-icons']
        },
        // Cleaner file names
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Chunk size warning limit
    chunkSizeWarningLimit: 1000
  },
  // Environment variables
  define: {
    'process.env': {}
  },
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-icons']
  },
  // Resolve aliases (optional)
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@hooks': '/src/hooks',
      '@utils': '/src/utils'
    }
  }
})
