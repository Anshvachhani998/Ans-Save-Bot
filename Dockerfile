FROM python:3.10-slim

WORKDIR /app


RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*


COPY . .


RUN pip install -r requirements.txt


CMD ["python", "bot.py"]
