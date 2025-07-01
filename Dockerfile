# Use a lightweight official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for Playwright browsers
RUN apt-get update && apt-get install -y \
    libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 \
    libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 wget gnupg curl ca-certificates fonts-liberation \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN pip install playwright && playwright install --with-deps

# Copy project files
COPY . .

# Expose port for gunicorn
EXPOSE 8000

# Run Django using Gunicorn
CMD ["gunicorn", "americatobd.wsgi:application", "--bind", "0.0.0.0:8000"]
