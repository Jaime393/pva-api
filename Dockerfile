FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install requests fastapi==0.95.1 uvicorn==0.22.0 python-multipart==0.0.6 pydantic==1.10.13
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
