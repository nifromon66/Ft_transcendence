FROM node:22-alpine

WORKDIR /app

RUN apk add --no-cache tini

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .

ENTRYPOINT [ "/sbin/tini", "--" ]
CMD ["npm", "run", "dev", "--", "--host"]
