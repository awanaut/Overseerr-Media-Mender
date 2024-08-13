FROM python:3.9-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENV RUN_INTERVAL=3600

CMD ["python", "omm.py"]