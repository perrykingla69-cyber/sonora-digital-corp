FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -q --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
