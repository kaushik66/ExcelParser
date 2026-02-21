FROM node:18-alpine

WORKDIR /app

# Copy the package dictionaries
COPY package.json package-lock.json* ./

# Install Node dependencies
RUN npm install

# Copy frontend source files
COPY . .

# Build the Next.js production bundle
RUN npm run build

# Expose the default Next.js port
EXPOSE 3000

# Serve the production application
CMD ["npm", "start"]
