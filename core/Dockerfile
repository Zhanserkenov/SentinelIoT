FROM python:3.12-slim

WORKDIR /app

COPY core/requirements.txt /app/core/requirements.txt
RUN pip install --no-cache-dir -r /app/core/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "core.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
