FROM python:3.10-slim

WORKDIR /app


RUN apt-get update && apt-get install -y git && apt-get clean

COPY . .


RUN pip install -r requirements.txt


CMD ["python", "bot.py"]
