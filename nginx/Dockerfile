FROM nginx:1.25.1-alpine

# Remove default nginx config and install required packages
RUN rm /etc/nginx/conf.d/default.conf \
    && apk add --no-cache openssl

# Generate self-signed certificates
RUN openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout /etc/ssl/private/cert.key \
    -out /etc/ssl/certs/cert.crt \
    -subj "/C=RU/ST=MSK/L=Moscow/O=TestY/OU=Development/CN=localhost"

# Create required directories and volumes directory structure
RUN mkdir -p /opt/testy/testy/testy-static \
    && mkdir -p /opt/testy/testy/media \
    && mkdir -p /opt/testy-frontend/build \
    && mkdir -p /opt/testy-frontend/build/static \
    && mkdir -p /data/volumes/media \
    && mkdir -p /data/volumes/build \
    && mkdir -p /data/volumes/pg-data \
    && mkdir -p /data/volumes/redis_data

# Create nginx configuration
RUN echo $'\
# Default configuration for HTTP to HTTPS redirect\n\
server {\n\
    listen 80 default_server;\n\
    server_name _;\n\
    return 301 https://$host$request_uri;\n\
}' > /etc/nginx/conf.d/default.conf

RUN echo $'\
server {\n\
    listen 443 ssl default_server;\n\
    charset utf-8;\n\
\n\
    ssl_certificate_key    /etc/ssl/private/cert.key;\n\
    ssl_certificate        /etc/ssl/certs/cert.crt;\n\
    server_name            ${HOST_NAME};\n\
    client_max_body_size 1000M;\n\
\n\
    root /opt/testy-frontend/build;\n\
    index index.html;\n\
    autoindex off;\n\
\n\
    # API endpoints\n\
    location ~ ^/(admin|api|api-auth|auth|swagger|plugins|celery-progress|attachments|avatars|sentry-debug)/ {\n\
        proxy_redirect off;\n\
        proxy_pass http://testy:8000;\n\
        proxy_set_header Host $http_host;\n\
        proxy_pass_request_body         on;\n\
        proxy_pass_request_headers      on;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
\n\
    # WebSocket connections\n\
    location ~ ^/(ws)/ {\n\
        proxy_pass http://testy:8000;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
    }\n\
\n\
    # Static files (build)\n\
    location /static/ {\n\
        alias /opt/testy-frontend/build/static/;\n\
        expires 30d;\n\
        add_header Cache-Control "public, no-transform";\n\
        access_log off;\n\
    }\n\
\n\
    # Static files (Django)\n\
    location /testy-static/ {\n\
        alias /opt/testy/testy/testy-static/;\n\
        expires 30d;\n\
        add_header Cache-Control "public, no-transform";\n\
        access_log off;\n\
    }\n\
\n\
    # Media files\n\
    location /media/ {\n\
        alias /opt/testy/testy/media/;\n\
        expires 30d;\n\
        add_header Cache-Control "public, no-transform";\n\
        access_log off;\n\
    }\n\
\n\
    # React app\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
        expires -1;\n\
        add_header Cache-Control "no-store, no-cache, must-revalidate";\n\
    }\n\
}\n\
\n\
server {\n\
    listen 80;\n\
    server_name    _;\n\
    return 301 https://$host$request_uri;\n\
}' > /etc/nginx/templates/testy-prod.conf.template

# Set permissions for volumes
RUN chmod -R 777 /data/volumes

# Set proper permissions
RUN chmod 644 /etc/ssl/certs/cert.crt \
    && chmod 640 /etc/ssl/private/cert.key \
    && chown -R nginx:nginx /opt/testy \
    && chown -R nginx:nginx /opt/testy-frontend \
    && chmod -R 755 /opt/testy \
    && chmod -R 755 /opt/testy-frontend

# Create a test index.html to avoid 403
RUN echo '<html><body>Loading...</body></html>' > /opt/testy-frontend/build/index.html \
    && chown nginx:nginx /opt/testy-frontend/build/index.html
