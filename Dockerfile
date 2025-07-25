FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY alembic.ini ./
COPY alembic ./alembic
COPY start.sh ./

RUN chmod +x start.sh

CMD ["./start.sh"] 