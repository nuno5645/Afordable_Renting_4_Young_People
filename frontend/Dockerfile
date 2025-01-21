FROM node:20-slim

WORKDIR /app

# Install required system dependencies for sharp
RUN apt-get update && apt-get install -y \
    python3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./

RUN npm install


COPY . .

# Remove any existing TypeScript config file to avoid conflicts
RUN rm -f pwa-assets.config.ts

# Generate PWA assets (includes icon generation)
RUN npm run generate-pwa-assets

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"] 