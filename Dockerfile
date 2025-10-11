FROM python:3.10-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY . .


RUN pip install -r requirements.txt


CMD ["python", "bot.py"]
