FROM node:alpine AS build-front
COPY ./ .
RUN yarn && yarn build

FROM python:3.11
WORKDIR /app
COPY --from=build-front dist ./dist
COPY pyproject.toml poetry.lock README.md ./
COPY meshroom ./meshroom
RUN pip install poetry && poetry install
CMD ["poetry", "run", "uvicorn", "meshroom.api.main:app", "--host", "0.0.0.0", "--port", "8000"]