FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

ENV TEST_ENV=dev
ENV PYTHONPATH=/app

CMD ["pytest", "-v", "--alluredir=allure-results"]
