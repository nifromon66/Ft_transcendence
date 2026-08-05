FROM nginx:alpine

RUN apk add --no-cache openssl

COPY conf/default.conf /etc/nginx/conf.d/default.conf
COPY tool/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]