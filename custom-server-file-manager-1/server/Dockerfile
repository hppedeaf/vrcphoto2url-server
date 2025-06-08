# Dockerfile for Railway deployment (optional - Railway auto-detects Python)
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create uploads directory
RUN mkdir -p uploads/files uploads/thumbnails

# Expose port
EXPOSE 8000

# Start command (Railway will override this with Procfile)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
