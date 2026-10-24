FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    FLASK_APP=run.py \
    UPLOAD_FOLDER=/data/uploads

WORKDIR /app
RUN useradd --create-home --uid 1000 ista
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data/uploads instance && chown -R ista:ista /data /app/instance /app/app/translations

USER ista
EXPOSE 8000
CMD ["sh", "docker-entrypoint.sh"]
