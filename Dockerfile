FROM python:3.10-slim

WORKDIR /app


RUN apt-get update && apt-get install -y

COPY . .


RUN pip install telethon
RUN pip install git+https://github.com/pytdbot/client.git
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
