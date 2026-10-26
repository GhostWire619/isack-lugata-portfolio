FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 JOURNAL_ENV=production
WORKDIR /app
COPY backend/requirements.lock ./requirements.lock
RUN pip install --no-cache-dir -r requirements.lock
COPY backend/ ./
COPY dist/sitemap.xml /app/portfolio-sitemap.xml
RUN DJANGO_SECRET_KEY=build-only-placeholder-key-not-used-at-runtime-01234567890123456789 DATABASE_URL=postgresql://build:build@localhost/build python manage.py collectstatic --noinput \
    && groupadd --gid 10001 journal && useradd --uid 10001 --gid journal --no-create-home journal \
    && mkdir -p /app/media && chown -R journal:journal /app/media
ENV PORTFOLIO_SITEMAP=/app/portfolio-sitemap.xml
USER journal
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=6 \
 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4)"
CMD ["gunicorn", "journal.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "90", "--access-logfile", "-", "--error-logfile", "-"]
