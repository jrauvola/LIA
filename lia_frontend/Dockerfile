# Start with a Node.js base image
FROM node:18-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies and include the missing babel plugin
RUN npm ci --only=production && \
    npm install --save-dev @babel/plugin-proposal-private-property-in-object && \
    npx update-browserslist-db@latest

# Copy the rest of your client application
COPY . .

# Build the application for production
RUN npm run build

# Use nginx with alpine for smaller image size
FROM nginx:alpine

# Copy nginx configuration if you have custom config
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Add security headers and gzip configuration
RUN echo 'server {\
    listen 80;\
    location / {\
        root /usr/share/nginx/html;\
        index index.html index.htm;\
        try_files $uri $uri/ /index.html;\
        add_header X-Frame-Options "SAMEORIGIN";\
        add_header X-XSS-Protection "1; mode=block";\
        add_header X-Content-Type-Options "nosniff";\
        gzip on;\
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;\
    }\
}' > /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]