FROM synthetixio/docker-node:16.14-alpine

RUN mkdir /app
WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "pm2-runtime", "npm", "--", "start" ]
