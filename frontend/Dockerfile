FROM node:18.13.0-alpine as builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.25.1-alpine as production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/build /opt/testy-frontend/build

# Copy nginx configuration
COPY ../nginx/testy-prod.conf.template /etc/nginx/templates/
COPY ../nginx/default.conf /etc/nginx/conf.d/

# Create directories and set permissions
RUN mkdir -p /opt/testy/testy/testy-static \
    && mkdir -p /opt/testy/testy/media \
    && chown -R nginx:nginx /opt/testy \
    && chown -R nginx:nginx /opt/testy-frontend \
    && chmod -R 755 /opt/testy \
    && chmod -R 755 /opt/testy-frontend