FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS='C:\Users\User\AppData\Roaming\gcloud\application_default_credentials.json'
CMD ["python", "publisher.py"]