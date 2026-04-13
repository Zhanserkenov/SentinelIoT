FROM python:3.12-slim
WORKDIR /app
COPY analyzer/requirements.txt /app/analyzer/requirements.txt
RUN pip install --no-cache-dir -r /app/analyzer/requirements.txt && \
    pip install uvicorn python-dotenv httpx sqlalchemy asyncpg \
    google-genai joblib numpy pandas scikit-learn
COPY . /app
EXPOSE 8001
CMD ["uvicorn", "analyzer.app.main:app", "--host", "0.0.0.0", "--port", "8001"]