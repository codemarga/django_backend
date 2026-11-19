# Multi-language Django Backend Dockerfile with C++ & Java support for Code Execution
FROM python:3.11-slim

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies:
# - g++ & build-essential: For compiling and executing C++ solutions
# - openjdk-17-jdk-headless: For compiling (javac) and executing (java) Java solutions
# - curl & netcat-openbsd: For network diagnostics & health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    openjdk-17-jdk-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
