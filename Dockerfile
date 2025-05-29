FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libportaudio2 \
    portaudio19-dev \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--factory", "-w", "3", "-b", "0.0.0.0:9000", "app:create_app"]
