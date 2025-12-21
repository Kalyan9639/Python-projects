# Use a slim Python image for smaller size and faster deployment
FROM python:3.10-slim

# Environment variables for Python performance and logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install essential system libraries for image/PDF processing (Pillow)
# These are MANDATORY for the bot to generate PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Add web server components for Render Free Tier compatibility
RUN pip install flask gunicorn

# Copy all project files
COPY . .

# Render's default port (Must be 10000)
ENV PORT=10000

# STARTUP COMMAND:
# 1. Runs your bot (manga_bot.py) in the background (&)
# 2. Runs Gunicorn (adsf.py) in the foreground to satisfy Render's port check
CMD python telegram_bot.py & gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 telegram_bot:app
