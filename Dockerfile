FROM python:3.10-slim

WORKDIR /app

RUN apt update && apt install -y ffmpeg aria2
RUN apt-get update && apt-get install -y git


COPY . .

RUN pip install -r requirements.txt
RUN pip install mtcute telethon tqdm
RUN pip install psycopg2-binary


CMD ["python", "bot.py"]
