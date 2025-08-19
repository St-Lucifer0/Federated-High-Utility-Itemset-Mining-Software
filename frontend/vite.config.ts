import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const serverUrl = env.VITE_SERVER_URL || 'http://localhost:8001';
  
  return {
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow external connections
    port: 3000,
    proxy: {
      '/api': {
        target: import.meta.env.VITE_SERVER_URL || 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: (import.meta.env.VITE_SERVER_URL || 'http://localhost:8001').replace('http', 'ws'),
        ws: true,
      }
    }
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
