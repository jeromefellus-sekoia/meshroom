yarn && yarn start &
exec poetry run uvicorn meshroom.api.main:app --host 127.0.0.1 --port 8001