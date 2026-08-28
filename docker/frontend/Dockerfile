FROM node:22-alpine

WORKDIR /app

RUN apk add --no-cache tini

COPY docker/frontend/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY src/frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY src/frontend .

ENTRYPOINT [ "/sbin/tini", "--", "entrypoint.sh" ]
CMD ["npm", "run", "dev", "--", "--host"]
#CMD ["sh", "-c", "npm run build && npm run preview -- --host --port 5173"]