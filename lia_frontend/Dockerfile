# Start with a Node.js base image
FROM node:18-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install all dependencies
RUN npm install

# Copy the rest of your client application
COPY . .

# Build the application for production
RUN npm run build

# Use nginx to serve the app on port 80
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
