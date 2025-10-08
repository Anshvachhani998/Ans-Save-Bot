FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Upgrade pip first
RUN python -m pip install --upgrade pip

# Install Python packages one by one
RUN pip install telethon
RUN pip install mtcute
RUN pip install tqdm
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
