docker build -t openai-feishu .
docker run --env-file .env -p 3000:3000 -it openai-feishu
