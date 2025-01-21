import sharp from 'sharp';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const publicDir = join(__dirname, '..', 'public');

const svgBuffer = readFileSync(join(publicDir, 'icon.svg'));

async function generateIcon() {
  await sharp(svgBuffer)
    .resize(512, 512)
    .toFile(join(publicDir, 'icon.png'));
  
  console.log('Icon generated successfully!');
}

generateIcon().catch(console.error); 