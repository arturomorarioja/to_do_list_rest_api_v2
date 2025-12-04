# Use a lightweight official Python image
FROM python:3.12-slim

# Do not generate .pyc files and make stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install system dependencies (optional but often useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "todos.py"]