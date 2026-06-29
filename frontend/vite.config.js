import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/Edustories/',
   build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        cabinet: resolve(__dirname, 'cabinet.html'),
        profile: resolve(__dirname, 'profile.html'),
      },
    },
  },
})