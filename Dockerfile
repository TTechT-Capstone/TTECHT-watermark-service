FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Pillow (image processing)
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create __init__.py files if they don't exist
RUN touch __init__.py && \
    touch controller/__init__.py && \
    touch service/__init__.py && \
    touch routes/__init__.py

# Test the app before starting
RUN python debug.py

EXPOSE 5000

ENV PORT=5000
ENV WORKERS=1
ENV PYTHONUNBUFFERED=1

# Start with fewer workers for debugging
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--log-level", "debug"]