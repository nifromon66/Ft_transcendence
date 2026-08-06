FROM nginx:alpine

RUN apk add --no-cache openssl

COPY conf/nginx.conf.template /etc/nginx/templates/default.conf.template
<<<<<<< HEAD
=======
# COPY tool/entrypoint.sh /entrypoint.sh
>>>>>>> f6cafbb (refactor(nginx):convert .conf to template for .env)
COPY tool/entrypoint.sh /docker-entrypoint.d/10-envsubst.sh
RUN chmod +x /docker-entrypoint.d/10-envsubst.sh

ENTRYPOINT ["/docker-entrypoint.d/10-envsubst.sh"]