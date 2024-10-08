FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENV INTERVAL=3600
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "omm.py"]