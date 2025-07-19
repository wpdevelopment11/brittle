FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir playwright
RUN playwright install --only-shell --with-deps chromium

COPY brittle.py /app

ENTRYPOINT ["python3", "brittle.py"]
