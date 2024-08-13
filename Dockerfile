FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENV RUN_INTERVAL=3600
ENV PYTHONUNBUFFERED=1
ENV FORCE_COLOR=1

CMD ["python", "-u", "omm.py"]