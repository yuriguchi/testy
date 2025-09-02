#!/bin/sh
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
-subj "/C=RU/ST=MSK" \
-keyout nginx-selfsigned.key -out nginx-selfsigned.crt