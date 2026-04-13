FROM python:3.12-slim
WORKDIR /app
COPY core/requirements.txt /app/core/requirements.txt
RUN pip install --no-cache-dir -r /app/core/requirements.txt && \
    pip install uvicorn asyncpg redis 'bcrypt==4.0.1' python-multipart \
    google-generativeai python-telegram-bot 'pydantic[email]' \
    alembic psycopg2-binary python-dotenv httpx python-jose \
    passlib apscheduler pandas
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "core.app.main:app", "--host", "0.0.0.0", "--port", "8000"]