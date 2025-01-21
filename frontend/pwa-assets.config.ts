import { defineConfig } from '@vite-pwa/assets-generator'

export default defineConfig({
  preset: {
    name: 'minimal',
    transparent: {
      sizes: [64, 192, 512]
    },
    maskable: {
      sizes: [512]
    },
    apple: {
      sizes: [180]
    }
  },
  images: ['public/icon.png']
}) 