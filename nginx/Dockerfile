FROM nginx:1.25.1-alpine

# Remove default nginx config and install required packages
RUN rm /etc/nginx/conf.d/default.conf \
    && apk add --no-cache openssl

# Generate self-signed certificates
RUN openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/ssl/private/cert.key \
    -out /etc/ssl/certs/cert.crt \
    -subj "/C=RU/ST=MSK/L=Moscow/O=TestY/OU=Development/CN=localhost" \
    && chmod 644 /etc/ssl/certs/cert.crt \
    && chmod 640 /etc/ssl/private/cert.key

# Copy nginx configuration
COPY testy-prod.conf.template /etc/nginx/templates/
COPY default.conf /etc/nginx/conf.d/
