# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# Set environment variables from .env file if it exists
# Note: For production, use proper secret management
# ENV BOT_TOKEN=your_bot_token
# ENV OPENROUTER_API_KEY=your_openrouter_key

# Command to run the bot
CMD ["python", "app.py"]
