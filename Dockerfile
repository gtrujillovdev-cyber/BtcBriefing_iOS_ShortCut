FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Solo dependencias del sistema mínimas para gráficos
RUN apt-get update && apt-get install -y \
    gcc \
    libfreetype6-dev \
    libpng-dev \
    libopenblas-dev     && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
