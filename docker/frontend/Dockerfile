FROM node:22-alpine

WORKDIR /app

RUN apk add --no-cache tini

COPY src/frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY src/frontend .

ENTRYPOINT [ "/sbin/tini", "--" ]
CMD ["npm", "run", "dev", "--", "--host"]