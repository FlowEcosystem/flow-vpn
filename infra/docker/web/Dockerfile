FROM node:22-alpine

WORKDIR /app

COPY apps/web/ ./

RUN if [ -f package-lock.json ]; then \
      npm ci; \
    elif [ -f package.json ]; then \
      npm install; \
    else \
      echo "apps/web has no package.json yet; dependency install skipped"; \
    fi

EXPOSE 3000

CMD ["sh", "-c", "if [ -f package.json ]; then npm run start; else echo 'apps/web has no package.json yet'; sleep infinity; fi"]
