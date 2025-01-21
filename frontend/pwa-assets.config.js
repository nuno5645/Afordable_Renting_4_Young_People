/** @type {import('@vite-pwa/assets-generator').GeneratePWAAssetsConfig} */
export default {
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
} 