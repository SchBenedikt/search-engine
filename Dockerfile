# Use python:3.8-slim as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the Docker image
COPY . /app

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download the 'stopwords' resource during the build process
RUN python -m nltk.downloader stopwords

# Add a health check to ensure the MongoDB connection is available before starting the Flask application
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl --fail http://localhost:5000/health || (echo "Datenbank nicht verfügbar, Anwendung nicht gestartet" && exit 1)

# Set the entry point to run the Flask application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
