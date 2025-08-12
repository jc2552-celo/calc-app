# Runtime-only image (no Playwright/browsers)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Only minimal system libs for FastAPI/uvicorn
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libx11-xcb1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# Install app deps ONLY (no playwright)
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir \
    fastapi==0.115.0 uvicorn[standard]==0.30.6 \
    SQLAlchemy==2.0.32 pydantic==2.8.2 pydantic-settings==2.4.0 \
    jinja2==3.1.4 python-multipart==0.0.9

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
