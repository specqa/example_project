FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY autotests/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем копируем весь код тестов
COPY autotests/ .

CMD ["pytest", "-v", "--alluredir=/app/allure-results"]