FROM python:3.10-slim

WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY . .


RUN pip install telethon
RUN pip install git+https://github.com/pytdbot/client.git
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
