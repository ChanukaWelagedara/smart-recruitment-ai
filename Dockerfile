# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy all source code
COPY . .

# Expose the port Flask/Gunicorn will run on
EXPOSE 5000

# Run the app using Gunicorn (production WSGI server)
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]