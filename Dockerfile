# Use a minimal Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency list first (layer caching — only re-runs pip if this file changes)
COPY requirements.txt .

# Install dependencies (--no-cache-dir keeps the image small)
RUN pip install --no-cache-dir flask==3.0.3

# Copy the application source code
COPY app.py .

# Document which port the app listens on (informational only)
EXPOSE 8080

# Command that runs when the container starts
CMD ["python", "app.py"]
